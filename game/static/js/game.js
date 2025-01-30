function getCSRFToken() {
  const cookies = document.cookie.split("; ");
  for (let cookie of cookies) {
    const [name, value] = cookie.split("=");
    if (name === "csrftoken") {
      return value;
    }
  }
  return null;
}

document.addEventListener("DOMContentLoaded", () => {
  const grid = document.getElementById("grid");
  const startButton = document.getElementById("start-game");
  const stopButton = document.getElementById("stop-simulation");
  const shuffleButton = document.getElementById("shuffle");
  const uploadButton = document.getElementById("upload-button");
  const imageInput = document.getElementById("image-upload");
  const algorithmButtons = document.querySelectorAll("input[name='algorithm']");
  const heuristicButtons = document.querySelectorAll("input[name='heuristic']");
  const sizeButtons = document.querySelectorAll("input[name='size']");
  const moveCounter = document.getElementById("move-counter"); // ✔️ Ispravljen brojač poteza
  const apiBaseUrl = "http://127.0.0.1:8000/game";

  let currentState = [];
  let goalState = [];
  let solving = false;
  let uploadedImage = "/static/img/example.png";
  let moveCount = 0;

  /**
   * Ažurira prikaz broja poteza.
   */
  function updateMoveCounter() {
    moveCounter.innerText = `Broj poteza: ${moveCount}`;
  }

  /**
   * Renderuje slagalicu na osnovu trenutnog stanja.
   */
  function renderGrid(state) {
    grid.innerHTML = "";
    const size = Math.sqrt(state.length);
    grid.style.gridTemplateColumns = `repeat(${size}, 100px)`;
    grid.style.gridTemplateRows = `repeat(${size}, 100px)`;

    state.forEach((tile, index) => {
      const div = document.createElement("div");
      div.className = "tile";

      if (tile === 0) {
        div.classList.add("empty");
      } else {
        div.style.backgroundImage = `url('${uploadedImage}')`;
        div.style.backgroundSize = `${size * 100}px ${size * 100}px`;
        div.style.backgroundPosition = `-${((tile - 1) % size) * 100}px -${
          Math.floor((tile - 1) / size) * 100
        }px`;
      }

      grid.appendChild(div);
    });
  }

  /**
   * Učitava početno i ciljno stanje sa backend-a.
   */
  async function fetchInitialAndGoalStates() {
    try {
      const size = document.querySelector("input[name='size']:checked").value;
      const response = await fetch(
        `${apiBaseUrl}/generate-states/?size=${size}`
      );
      if (!response.ok)
        throw new Error("Failed to fetch initial and goal states.");

      const data = await response.json();
      console.log("Received initial state:", data.initial_state);
      console.log("Received goal state:", data.goal_state);

      currentState = data.initial_state;
      goalState = data.goal_state;

      renderGrid(currentState);
    } catch (error) {
      console.error("Error fetching states:", error);
    }
  }

  /**
   * Nasumično meša trenutno stanje.
   */
  function shuffleGrid() {
    let shuffledState;
    do {
      shuffledState = [...goalState];
      let currentIndex = shuffledState.length;

      while (currentIndex !== 0) {
        const randomIndex = Math.floor(Math.random() * currentIndex);
        currentIndex--;

        [shuffledState[currentIndex], shuffledState[randomIndex]] = [
          shuffledState[randomIndex],
          shuffledState[currentIndex],
        ];
      }
    } while (!isSolvable(shuffledState));

    currentState = shuffledState;
    renderGrid(currentState);
    moveCount = 0;
    updateMoveCounter();
  }

  /**
   * Provera da li je stanje rešivo.
   */
  function isSolvable(state) {
    let inversions = 0;
    const size = Math.sqrt(state.length);

    for (let i = 0; i < state.length; i++) {
      for (let j = i + 1; j < state.length; j++) {
        if (state[i] > state[j] && state[i] !== 0 && state[j] !== 0) {
          inversions++;
        }
      }
    }

    if (size % 2 === 1) {
      return inversions % 2 === 0;
    } else {
      const emptyRow = Math.floor(state.indexOf(0) / size);
      return (inversions + emptyRow) % 2 === 1;
    }
  }

  /**
   * Pokreće rešavanje slagalice.
   */
  async function solvePuzzle() {
    const algorithm =
      Array.from(algorithmButtons).find((btn) => btn.checked)?.value || "astar";
    const heuristic =
      Array.from(heuristicButtons).find((btn) => btn.checked)?.value ||
      "manhattan";
    const size = document.querySelector("input[name='size']:checked").value;

    const data = {
      initial_state: currentState,
      goal_state: goalState,
      algorithm,
      heuristic,
      size: parseInt(size),
      image: uploadedImage,
    };

    console.log("Sending data to backend:", data);

    try {
      const response = await fetch(`${apiBaseUrl}/solve-with-image/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCSRFToken(),
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error("Server error:", errorData.error);
        return;
      }

      const result = await response.json();
      console.log("Solution steps received:", result.solution_steps);

      if (!result.solution_steps || !Array.isArray(result.solution_steps)) {
        console.error(
          "Invalid response: solution_steps is missing or not an array."
        );
        return;
      }

      let stepIndex = 0;
      solving = true;
      moveCount = 0;
      updateMoveCounter();

      function playNextStep() {
        if (!solving || stepIndex >= result.solution_steps.length) {
          console.log("Puzzle solved!");
          return;
        }

        console.log("Applying move:", result.solution_steps[stepIndex]);

        currentState = applyAction(
          currentState,
          result.solution_steps[stepIndex]
        );
        renderGrid(currentState);
        moveCount++;
        updateMoveCounter();
        stepIndex++;

        setTimeout(playNextStep, 500);
      }

      playNextStep();
    } catch (error) {
      console.error("Error solving puzzle:", error);
    }
  }

  /**
   * Uploaduje sliku i ažurira slagalicu.
   */
  uploadButton.addEventListener("click", async () => {
    if (imageInput.files.length === 0) {
      alert("Molimo odaberite sliku.");
      return;
    }

    const formData = new FormData();
    formData.append("image", imageInput.files[0]);

    try {
      const response = await fetch(`${apiBaseUrl}/upload-image/`, {
        method: "POST",
        body: formData,
      });

      const result = await response.json();
      if (result.image_url) {
        uploadedImage = result.image_url; // ✔ Koristi pravu putanju
        alert("Slika uspešno uploadovana!");
        fetchInitialAndGoalStates(); // ✔ Ponovno učitavanje stanja sa novom slikom
      } else {
        alert("Greška pri uploadovanju slike.");
      }
    } catch (error) {
      console.error("Error uploading image:", error);
    }
  });

  /**
   * Primena poteza na trenutno stanje.
   */
  function applyAction(state, action) {
    console.log("Applying action:", action);
    const newState = [...state];
    const zeroIndex = state.indexOf(0);

    if (action < 0 || action >= newState.length) {
      console.error("Invalid action:", action);
      return state;
    }

    [newState[zeroIndex], newState[action]] = [
      newState[action],
      newState[zeroIndex],
    ];
    return newState;
  }

  startButton.addEventListener("click", solvePuzzle);
  stopButton.addEventListener("click", () => (solving = false));
  shuffleButton.addEventListener("click", shuffleGrid);
  sizeButtons.forEach((button) =>
    button.addEventListener("change", fetchInitialAndGoalStates)
  );

  fetchInitialAndGoalStates();
});
