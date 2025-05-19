document.getElementById("tokenForm").addEventListener("submit", function (e) {
    e.preventDefault();

    const token = document.getElementById("token").value;
    const messageElement = document.getElementById("message");
    const button = document.querySelector("button");

    messageElement.textContent = "実行中...";
    button.disabled = true;

    fetch("/start", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams({ token: token }),
    })
    .then(response => response.json())
    .then(data => {
        messageElement.textContent = data.log.trim() || "ログがありません";
    })
    .catch(() => {
        messageElement.textContent = "通信エラーが発生しました。";
    })
    .finally(() => {
        button.disabled = false;
    });
});
