window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: function(n_clicks) {
            navigator.clipboard.writeText(document.getElementById('llm-summary').innerText);
            return "";
        }
    }
});