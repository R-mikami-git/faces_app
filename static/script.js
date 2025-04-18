//汎用アラート
async function showWhileTask(taskFunction) {
    // 処理中のメッセージ要素を作成
    let processingMessage = document.createElement("div");
    processingMessage.id = "processingMessage"; // IDを指定
    processingMessage.textContent = "処理実行中..."; // メッセージを設定
    document.body.appendChild(processingMessage); // 要素を追加

    try {
        await taskFunction(); // タスクを実行
    } catch (error) {
        console.error("エラーが発生しました:", error);
    } finally {
        // 処理終了後にメッセージを削除
        document.body.removeChild(processingMessage);
    }
}

//登録ボタン
function register() {
    var form = document.getElementById('register-form');
    form.style.display = 'block';
}

// 送信ボタンの処理
function recordFace() {
    const attendanceBtn = document.getElementById('attendanceBtn');
    const leaveBtn = document.getElementById('leaveBtn');
    const recordBtn = document.getElementById('recordBtn');

    // ボタンを無効化
    attendanceBtn.disabled = true;
    leaveBtn.disabled = true;
    recordBtn.disabled = true;

    showWhileTask(() => {
        return fetch('/recordFace', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                class: document.getElementById('class').value,
                studentNumber: document.getElementById('student_number').value,
                name: document.getElementById('name').value
            })
        })
        .then(response => response.text())
        .then(serverResponse => {
            alert(serverResponse); // サーバーからのレスポンスを表示
            if (serverResponse.includes("登録しました")) {
                document.getElementById('register-form').style.display = 'none';
            }
            // 処理完了後にボタンを復帰
            attendanceBtn.disabled = false;
            leaveBtn.disabled = false;
            recordBtn.disabled = false;
        })
        .catch(error => {
            console.error("エラーが発生しました:", error);
            alert("エラーが発生しました。"); // エラーメッセージを表示
            // エラー発生時もボタンを復帰
            attendanceBtn.disabled = false;
            leaveBtn.disabled = false;
            recordBtn.disabled = false;
        });
    });
}


//戻るボタン
function cancel(){
    document.getElementById('register-form').style.display = 'none';
}

// 出席ボタンの処理
function recordAttendance() {
    const attendanceBtn = document.getElementById('attendanceBtn');
    const leaveBtn = document.getElementById('leaveBtn');
    const recordBtn = document.getElementById('recordBtn');

    // 出席ボタンを無効化し、退席ボタンを有効化
    attendanceBtn.disabled = true;
    leaveBtn.disabled = true;
    recordBtn.disabled = true;

    showWhileTask(() => {
        return fetch('/attendance', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.text())
        .then(serverResponse => {
            alert(serverResponse); // サーバーからのレスポンスを表示
            // 処理完了後にボタンを復帰
            attendanceBtn.disabled = false;
            leaveBtn.disabled = false;
            recordBtn.disabled = false;
        })
        .catch(error => {
            console.error("エラーが発生しました:", error);
            alert("エラーが発生しました。");
            // エラー発生時もボタンを復帰
            attendanceBtn.disabled = false;
            leaveBtn.disabled = false;
            recordBtn.disabled = false;
        });
    });
}

// 退席ボタンの処理
function recordAway() {
    const attendanceBtn = document.getElementById('attendanceBtn');
    const leaveBtn = document.getElementById('leaveBtn');
    const recordBtn = document.getElementById('recordBtn');

    // 退席ボタンを無効化し、出席ボタンを有効化
    attendanceBtn.disabled = true;
    leaveBtn.disabled = true;
    recordBtn.disabled = true;

    showWhileTask(() => {
        return fetch('/recordAway', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.text())
        .then(serverResponse => {
            alert(serverResponse); // サーバーからのレスポンスを表示
            // 処理完了後にボタンを復帰
            attendanceBtn.disabled = false;
            leaveBtn.disabled = false;
            recordBtn.disabled = false;
        })
        .catch(error => {
            console.error("エラーが発生しました:", error);
            alert("エラーが発生しました。");
            // エラー発生時もボタンを復帰
            attendanceBtn.disabled = false;
            leaveBtn.disabled = false;
            recordBtn.disabled = false;
        });
    });
}
//設定ボタン
function setting() {
    window.location.href = "/login"; 
}


//ここからログイン画面


//ログインボタン
function login() {

    var username = document.getElementById("username").value;
    var password = document.getElementById("password").value;

    if (!username || !password) {
        alert("すべての入力欄を埋めてください");
        return;
    }

    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            username: username,
            password: password
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = "setting"; // ログイン成功時にページ移動
        } else {
            alert(data.message || "ログインに失敗しました"); // エラーメッセージを表示
        }
    })
    .catch(error => {
        console.error("エラーが発生しました:", error);
        alert("データ送信中にエラーが発生しました。再度お試しください。");
    });
}


//ここから設定画面


//ソートボタン
function sortTable(columnIndex) {
    const table = document.querySelector("table"); // ソート対象のテーブル
    const rows = Array.from(table.rows).slice(1); // ヘッダーを除いた行を取得
    const isAscending = table.dataset.sortOrder === "asc"; // 昇順/降順を判定
    const direction = isAscending ? 1 : -1; // 昇順なら 1、降順なら -1

    // ソートロジック
    rows.sort((rowA, rowB) => {
        const cellA = rowA.cells[columnIndex].innerText.toLowerCase();
        const cellB = rowB.cells[columnIndex].innerText.toLowerCase();

        // 数値としてソートするか、文字列としてソートするか判定
        const valueA = isNaN(cellA) ? cellA : parseFloat(cellA);
        const valueB = isNaN(cellB) ? cellB : parseFloat(cellB);

        // 比較ロジック
        if (valueA > valueB) return direction;
        if (valueA < valueB) return -direction;
        return 0; // 同じ場合
    });

    // ソート結果をテーブルに反映
    rows.forEach(row => table.tBodies[0].appendChild(row));

    // 昇順/降順を切り替え
    table.dataset.sortOrder = isAscending ? "desc" : "asc";
}

//setting 送信ボタン
function data_transmission() {

    var classInput = document.getElementById('class').value;
    var nameInput = document.getElementById('name').value;
    var checkDayInput = document.getElementById('check_day').value;

    if (!classInput && !nameInput && !checkDayInput ) {
        alert("いずれかの項目を入力してください");
        return; // 処理を中断
    }
    
    console.log("入力値:",
        classInput, 
        nameInput,
        checkDayInput,
    );

    // データ送信開始時のアラート
    alert("データ送信中です...");

    fetch('/data_transmission', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            class: classInput,
            name: nameInput,
            checkDay:checkDayInput,
        })
    })

    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTPエラー: ${response.status}`);
        }
        return response.json(); // JSON形式のレスポンスをパース
    })
    .then(responseData => {
        if (responseData.length === 0) {
            // 値が存在しない場合のアラート
            alert("検索結果が見つかりませんでした");
        } else {
            // 検索結果がある場合にテーブルを更新
            const tableBody = document.querySelector('.data_table tbody');
            tableBody.innerHTML = '';
    
            responseData.forEach(row => {
                const newRow = `
                    <tr>
                        <td>${row["ユーザーcd"]}</td>
                        <td>${row["クラス"]}</td>
                        <td>${row["出席番号"]}</td>
                        <td>${row["名前"]}</td>
                        <td>${row["日付"]}</td>
                        <td>${row["出席時間"]}</td>
                        <td>${row["退席時間"]}</td>
                        <td>${row["ステータス"]}</td>
                    </tr>
                `;
                tableBody.insertAdjacentHTML('beforeend', newRow);
            });
        }
    })
    .catch(error => {
        console.error('エラーが発生しました:', error);
        alert("データ送信中にエラーが発生しました：" + error.message);
    });
}

//クリアボタン
function clear_form() {
    window.location.href = "/setting"; 
}

//インデックスに戻る
function index_back() {
    window.location.href = "/"; 
}