# blabla

blabla


<div id="click-me">Click me!</div>

<script>
  document.getElementById('click-me').onclick = () => {
    document.getElementById('click-me').innerHTML = "Clicked!";
    console.log("Div clicked!");
  };
</script>

<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>

<script>
  const aInput = document.getElementById("a");
  const bInput = document.getElementById("b");
  const output = document.getElementById("output");

  function updateEquation() {
    const a = parseFloat(aInput.value);
    const b = parseFloat(bInput.value);
    if (isNaN(a) || isNaN(b)) {
      output.textContent = ""; // clear output
      return;
    }

    const y = a * Math.pow(b, 2);
    const latex = `y = a \\cdot b^2 = ${a} \\cdot ${b}^2 = ${y}`;
    output.innerHTML = `\\(${latex}\\)`;
    MathJax.typesetPromise([output]);
  }

  // Live updates as user types
  aInput.addEventListener("input", updateEquation);
  bInput.addEventListener("input", updateEquation);

  // Initialize display
  updateEquation();
</script>
 

<style>
  label {
    margin-right: 0.5em;
  }
  input[type="number"] {
    margin: 0.5em 1em 1em 0;
    padding: 0.4em;
    font-size: 1em;
  }
  input:invalid {
    border: 2px solid red;
  }
  input:valid {
    border: 2px solid green;
  }
  #output {
    font-size: 1.3em;
    margin-top: 1em;
  }
</style>

## Live: $y = a \cdot b^2 $

<label for="a">a:</label>
<input type="number" id="a" value="2" min="0" step="any" required>

<label for="b">b:</label>
<input type="number" id="b" value="3" min="0" step="any" required>

<p id="output"></p>



