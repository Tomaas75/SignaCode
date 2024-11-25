$(document).ready(function () {
    console.log("Script de animaciones cargado correctamente.");

    // 1. Animación de bienvenida (fade-in con zoom)
    $(".welcome-box").css({ opacity: 0, transform: "scale(0.9)" }).animate({ opacity: 1 }, 800, function () {
        $(this).css("transform", "scale(1)");
    });

    // 2. Animación de bienvenida en el texto
    $(".welcome-box h1").hide().fadeIn(2000);

    // 3. Deslizamiento para la información del usuario
    $(".user-info").hide().slideDown(1000);

    // 4. Efecto hover en botones y enlaces
    $(".btn, .options a").hover(
        function () {
            $(this).css({
                transform: "scale(1.1)",
                transition: "transform 0.3s ease",
                backgroundColor: "#FFD700",
                color: "#000"
            });
        },
        function () {
            $(this).css({
                transform: "scale(1)",
                backgroundColor: "",
                color: ""
            });
        }
    );

    // 5. Animación al hacer clic en opciones
    $(".options a").on("click", function (e) {
        e.preventDefault();
        const link = $(this).attr("href");
        $("body").fadeOut(500, function () {
            window.location.href = link;
        });
    });

    // 6. Footer deslizándose desde abajo
    $("footer").css({ opacity: 0, position: "relative", bottom: "-50px" }).animate({
        opacity: 1,
        bottom: "0px"
    }, 1000);

    // 7. Animación al hacer clic en "Cerrar sesión"
    $(".btn.danger").on("click", function () {
        $(this).animate({ opacity: 0.7 }, 200).fadeOut(300);
    });

    // 8. Animación de scroll suave al hacer clic en los enlaces del menú
    $("nav ul li a").on("click", function (event) {
        event.preventDefault();
        const target = $(this.getAttribute("href"));
        if (target.length) {
            $("html, body").stop().animate({
                scrollTop: target.offset().top
            }, 1000);
        }
    });
});
