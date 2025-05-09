from dataclasses import dataclass, field
from typing import List
import numpy as np
from ......codes.usa.atc40.raw.ch8 import csm as csm_atc40
# from ...raw.ch8 import csm as csm_atc40
from ......common.math.numerical import intersection
from ......common.io.output import OutputTable, OutputExtended
from ......tools.bilin import Bilin, BilinearCurve
from ......codes.eurocodes.ec8.cls.seismic_action import spectra as spec_ec8


@dataclass
class StructureProperties:
    φ: np.ndarray
    m: np.ndarray
    T0: float
    pushover_curve_F: np.ndarray
    pushover_curve_δ: np.ndarray
    behavior: str

    def __post_init__(self):
        self.PF1 = csm_atc40.PF1(self.m, self.φ)
        self.α1 = csm_atc40.α1(self.m, self.φ)
        self.φroof1 = self.φ[-1]
        self.Sa = csm_atc40.Sa(V=self.pushover_curve_F,
                               W=sum(self.m),
                               α1=self.α1)
        self.Sd = csm_atc40.Sd(Δroof=self.pushover_curve_δ,
                               PF1=self.PF1,
                               φroof1=self.φroof1)


@dataclass
class Demand:
    T_range: np.ndarray
    Sa: np.ndarray
    Sd: np.ndarray
    TC: float

    def ec8_elastic(self, αgR: float, γI: float, ground_type: str, spectrum_type: int, η=1.0, q=1.0, β=0.2):
        _spec_ec8 = spec_ec8.SpectraEc8(αgR, γI, ground_type, spectrum_type, η, q, β)
        self.Sa = _spec_ec8.Se(self.T_range)
        self.Sd = _spec_ec8.SDe(self.T_range)
        self.TC = _spec_ec8.TC


@dataclass
class CapacitySpectrumMethod:
    structure: StructureProperties
    demand: Demand
    first_try_case: str = 'intersection'
    max_iterations: int = 50
    tolerance: float = 0.0001
    
    def __post_init__(self):
        self.output = OutputTable()
        self.performance_point = None
    
    @property
    def Sd_first_try(self):
        if self.first_try_case == 'intersection':
            x_solve, y_solve = intersection(self.demand.Sd, self.demand.Sa, self.structure.Sd, self.structure.Sa)
            return x_solve[-1] if len(x_solve) > 0 else None
        elif self.first_try_case == 'equal displacements':
            Sd_T0 = 100.
            Sa_T0 = Sd_T0 * (2 * np.pi / self.structure.T0) ** 2
            Sa_T0_array = np.array([0.0, Sa_T0])
            Sd_T0_array = np.array([0.0, Sd_T0])
            xT0_solve, yT0_solve = intersection(self.demand.Sd, self.demand.Sa, Sd_T0_array, Sa_T0_array)
            return xT0_solve[-1] if len(xT0_solve) > 0 else None
        else:
            raise ValueError(f"Unknown first_try_case: {self.first_try_case}")

    def __iterate_SR(self, x0):
        """Calculate the next iteration point using spectral reduction factors"""
        bl = Bilin(xtarget=x0)
        bl.curve_ini.x, bl.curve_ini.y = self.structure.Sd, self.structure.Sa
        bl.calc()

        β0 = bl.bilinear_curve.β0
        βeff = csm_atc40.βeff(0.05, β0, self.structure.behavior)
        Teff = bl.bilinear_curve.Teq(self.structure.T0)

        # Select appropriate reduction factor based on period
        SRA = csm_atc40.SRA(βeff, self.structure.behavior)
        SRV = csm_atc40.SRV(βeff, self.structure.behavior)
        SR = SRV if Teff > self.demand.TC else SRA

        # Apply reduction to demand spectrum
        _Sa = SR * self.demand.Sa
        _Sd = SR * self.demand.Sd

        # Find intersection with capacity curve
        x_solve, y_solve = intersection(_Sd, _Sa, self.structure.Sd, self.structure.Sa)
        
        # Return the last intersection point or None if no intersection
        return x_solve[-1] if len(x_solve) > 0 else None

    def calc_performance_point(self):
        """Calculate the performance point through iteration"""
        self.output.data.clear()
        
        # Get initial estimate
        x_i = self.Sd_first_try
        if x_i is None:
            raise ValueError("Could not determine initial displacement estimate")
        
        iter_num = 0
        error = float('inf')
        self.output.data.append({'__iteration': iter_num, 'Sd': x_i, 'error': None})
        
        # Iteration loop
        while error > self.tolerance and iter_num < self.max_iterations:
            x_new = self.__iterate_SR(x_i)
            
            # Check for convergence failure
            if x_new is None:
                raise ValueError(f"No intersection found at iteration {iter_num}")
                
            error = abs((x_new - x_i) / x_i) if x_i != 0 else abs(x_new)
            x_i = x_new
            iter_num += 1

            self.output.data.append({'__iteration': iter_num, 'Sd': x_i, 'error': error})
            
        # Check if we reached max iterations without converging
        if iter_num == self.max_iterations and error > self.tolerance:
            print(f"Warning: Maximum iterations ({self.max_iterations}) reached with error = {error:.4f}")
        
        self.performance_point = {'Sd': x_i, 'Sa': np.interp(x_i, self.structure.Sd, self.structure.Sa)}
        print(f'Solution: Sd = {x_i:.4f}m, Sa = {self.performance_point["Sa"]:.4f}g')
        
        return self.performance_point



@dataclass
class CapacitySpectrumMethodProcedureB:
    """
    incomplete...check jupyter notebook
    """
    structure: StructureProperties
    demands: List[Demand] = field(default_factory=list)
    dstar: float = None
    astar: float = None
    bilinear_curve: BilinearCurve = None


    def __post_init__(self):
        self.output = OutputTable()

    def calc_performance_point(self):
        self.dstar_intersection = self._get_dstar()
        self.bilinear_curve = self._get_bilinear_curve()
        self.astar = self.bilinear_curve.au
        self._try_more_points()




    def _get_dstar(self):
        bl = Bilin()
        bl.curve_ini.x = self.structure.Sd
        bl.curve_ini.y = self.structure.Sa
        bl.calc()

        kel = bl.bilinear_curve.kel
        x_kel = np.array([0., 10.])
        y_kel = np.array([0., 10. * kel])

        _dstar, _adstar = intersection(x_kel, y_kel, self.demands[0]['demand'].Sd, self.demands[0]['demand'].Sa)
        self.dstar = _dstar[0]

        return _dstar[0], _adstar[0]


    def _get_bilinear_curve(self):
        bl = Bilin(xtarget=self.dstar)
        bl.curve_ini.x = self.structure.Sd
        bl.curve_ini.y = self.structure.Sa
        bl.calc()
        return bl.bilinear_curve

    def _try_more_points(self):
        self.dpi_rng = np.linspace(0.5 * self.dstar, 1.5 * self.dstar, 11)
        self.api_rng = self._api(self.astar, self.dstar, self.bilinear_curve.ay, self.bilinear_curve.dy, self.dpi_rng)
        self.β0_rng = csm_atc40.β0(self.bilinear_curve.dy, self.bilinear_curve.ay, self.dpi_rng, self.api_rng)
        self.βeff_rng = np.array([csm_atc40.βeff(0.05, x, self.structure.behavior) for x in  self.β0_rng])




    @staticmethod
    def _api(astar, dstar, ay, dy, dpi):
        return ay + (astar - ay) * (dpi - dy) / (dstar - dy)


