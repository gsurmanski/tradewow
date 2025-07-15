//main file for basic functionality across site
document.addEventListener("DOMContentLoaded", () => {
    const profile = document.querySelector("#profile_icon");
    const dropdown = document.querySelector("#profile_dropdown");

    profile.addEventListener("click", (e) => {
        e.stopPropagation(); // Prevent this click from triggering the document listener
        dropdown.style.display = "block";
    });

    document.addEventListener("click", () => {
            dropdown.style.display = "none";
    });
});