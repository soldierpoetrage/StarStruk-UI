document.getElementById("planetForm").addEventListener("submit", function(event) {
    event.preventDefault();
    const selectedPlanet = document.getElementById("exoplanet").value;

    // Example of handling the selection
    fetch(`/planet_data?planet=${selectedPlanet}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById("planetData").innerHTML = `
                <h2>${data.name}</h2>
                <p>${data.description}</p>
            `;
        });
});
