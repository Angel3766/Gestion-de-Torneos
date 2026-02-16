document.addEventListener("DOMContentLoaded", () => {

    const buttons = document.querySelectorAll(".delete-btn");

    buttons.forEach(btn => {
        btn.addEventListener("click", (e) => {

            if (!confirm("¿Seguro que deseas eliminar este elemento?")) {
                e.preventDefault();
            }

        });
    });

});
