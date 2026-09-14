// Login com Google (Firebase Authentication).
//
// O template injeta window.FIREBASE_CONFIG (so quando as chaves existem) junto
// com o SDK compat. Em clique: popup do Google -> ID token -> form#form-google
// (csrf_token + id_token) -> POST /entrar-google, que valida no servidor.
(function () {
    'use strict';

    var config = window.FIREBASE_CONFIG;
    var botao = document.getElementById('botao-google');
    if (!config || !botao) {
        return; // Firebase não configurado — nada a fazer.
    }

    firebase.initializeApp(config);
    var provider = new firebase.auth.GoogleAuthProvider();

    botao.addEventListener('click', function () {
        botao.disabled = true; // evita clique duplo durante o popup

        firebase.auth().signInWithPopup(provider)
            .then(function (resultado) {
                return resultado.user.getIdToken();
            })
            .then(function (idToken) {
                document.getElementById('id-token').value = idToken;
                document.getElementById('form-google').submit();
            })
            .catch(function (erro) {
                botao.disabled = false;
                // Fechar o popup ou negar acesso não é erro do site — silêncio.
                if (erro && (erro.code === 'auth/popup-closed-by-user'
                          || erro.code === 'auth/cancelled-popup-request')) {
                    return;
                }
                alert('Não foi possível entrar com o Google: ' + (erro && erro.message ? erro.message : 'erro desconhecido.'));
            });
    });
})();