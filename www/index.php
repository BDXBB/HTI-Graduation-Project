<?php
// ============================================================
// index.php — داشبۆردی سەرەکی
// - خوێندنەوەی داتا ڕاستەوخۆ لە DB
// - دوبارە بارکردنی پەڕە هەر 20 چرکە
// ============================================================

$host = 'localhost';
$user = 'g7admin';
$pass = '1234g7';
$db   = 'hti_Automation';

// مامەڵەکردن بە داواکاریی POST — نوێکردنەوەی دۆخی ئامێر
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $device    = $_POST['device']     ?? '';
    $newStatus = $_POST['new_status'] ?? '';

    if ($device && $newStatus) {
        $c = mysqli_connect($host, $user, $pass, $db);
        mysqli_query($c, "UPDATE device_status SET status='$newStatus' WHERE device_name='$device'");
        mysqli_close($c);
    }
    header("Location: index.php");
    exit;
}

// خوێندنەوەی هەموو دۆخەکان لە
//  داتا بەیس
$conn   = mysqli_connect($host, $user, $pass, $db);
$result = mysqli_query($conn, "SELECT device_name, status FROM device_status");
$data   = [];
while ($row = mysqli_fetch_assoc($result)) {
    $data[$row['device_name']] = $row['status'];
}
mysqli_close($conn);


function st($data, $key, $default = '...') {
    return $data[$key] ?? $default;
}
function isOn($data, $key) {
    return isset($data[$key]) && $data[$key] === 'ON';
}
?>
<!DOCTYPE html>
<html lang="ckb" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HTI Smart Home — داشبۆرد</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="css/style.css">
    <style>
        .badge-detected { background:#c0392b; color:#fff; padding:6px 14px; border-radius:20px; font-weight:700; }
        .badge-safe     { background:#27ae60; color:#fff; padding:6px 14px; border-radius:20px; font-weight:700; }
        .badge-open     { background:#e67e22; color:#fff; padding:6px 14px; border-radius:20px; font-weight:700; }
        .badge-closed   { background:#27ae60; color:#fff; padding:6px 14px; border-radius:20px; font-weight:700; }
        .btn-reset      { background:#c0392b; color:#fff; border:none; padding:8px 20px;
                          border-radius:8px; cursor:pointer; margin-top:10px;
                          font-family:Cairo,sans-serif; font-size:14px; }
        .btn-reset:hover{ background:#a93226; }
                          z-index:9999; animation: shrink 20s linear forwards; }
        @keyframes shrink { from{width:100%} to{width:0%} }
        #countdown      { font-size:12px; opacity:0.6; margin-top:4px; }
        footer          { text-align:center; padding:20px; opacity:0.7; font-size:13px; }
    </style>
</head>
<body>

    <!-- هێدەر -->
    <header>
        <div class="header-icon">🏠</div>
        <p>Smart Home &amp; Security</p>
    </header>

    <main class="dashboard">

        <!--    سیستەمی پاراستن -->
        <div class="card <?= isOn($data,'security_system') ? 'card-active' : '' ?>">
            <div class="card-icon">🛡️</div>
            <h2>سیستەمی پاراستن</h2>
            <p class="card-desc">چالاک کردن یان ناچالاک کردنی دۆخی پاراستن</p>
            <form method="POST" action="index.php">
                <input type="hidden" name="device" value="security_system">
                <input type="hidden" name="new_status" value="<?= isOn($data,'security_system') ? 'OFF' : 'ON' ?>">
                <button type="submit" class="toggle-btn <?= isOn($data,'security_system') ? 'btn-on' : '' ?>">
                    <?= isOn($data,'security_system') ? 'چالاکە 🟢' : 'ناچالاکە 🔴' ?>
                </button>
            </form>
        </div>

        <!-- light -->
        <div class="card <?= isOn($data,'light') ? 'card-on' : '' ?>">
            <div class="card-icon">💡</div>
            <h2>light</h2>
            <p class="card-desc">light</p>
            <form method="POST" action="index.php">
                <input type="hidden" name="device" value="light">
                <input type="hidden" name="new_status" value="<?= isOn($data,'light') ? 'OFF' : 'ON' ?>">
                <button type="submit" class="toggle-btn <?= isOn($data,'light') ? 'btn-on' : '' ?>">
                    <?= isOn($data,'light') ? 'کوژانەوە' : 'داگرساندن' ?>
                </button>
            </form>
        </div>

        <!-- هەستکەری جووڵە PIR -->
        <?php $pirStatus = st($data,'pir_1','SAFE'); $pirDanger = ($pirStatus === 'DETECTED'); ?>
        <div class="card <?= $pirDanger ? 'card-active' : '' ?>">
            <div class="card-icon">🏃</div>
            <h2>هەستکەری جووڵە</h2>
            <p class="card-desc">PIR Sensor</p>
            <span class="<?= $pirDanger ? 'badge-detected' : 'badge-safe' ?>">
                <?= $pirDanger ? '⚠️ جووڵە هەیە!' : '✅ سەلامەت' ?>
            </span>
        </div>

        <!-- هەستکەری گاز MQ-2 + دوگمەی ڕیسێت -->
        <?php $gasStatus = st($data,'gas_sensor','SAFE'); $gasDanger = ($gasStatus === 'DETECTED'); ?>
        <div class="card <?= $gasDanger ? 'card-active' : '' ?>">
            <div class="card-icon">🎇</div>
            <h2>هەستکەری گاز</h2>
            <p class="card-desc">MQ-2 — دۆزینەوەی گاز</p>
            <span class="<?= $gasDanger ? 'badge-detected' : 'badge-safe' ?>">
                <?= $gasDanger ? '🚨 ئاگاداری! گاز بونی هەیە!' : '✅ سەلامەت' ?>
            </span>
            <?php if ($gasDanger): ?>
            <form method="POST" action="index.php" style="margin-top:10px">
                <input type="hidden" name="device"     value="gas_sensor">
                <input type="hidden" name="new_status" value="SAFE">
                <button type="submit" class="btn-reset">🔄 ڕیسێتی ئاگادارکردنەوە</button>
            </form>
            <?php endif; ?>
        </div>

        <!-- دەرگا MC-38 -->
        <?php $doorStatus = st($data,'door_sensor','CLOSED'); $doorOpen = ($doorStatus === 'OPEN'); ?>
        <div class="card <?= $doorOpen ? 'card-active' : '' ?>">
            <div class="card-icon">🚪</div>
            <h2>دەرگا</h2>
            <p class="card-desc">MC-38</p>
            <span class="<?= $doorOpen ? 'badge-open' : 'badge-closed' ?>">
                <?= $doorOpen ? '⚠️ کراوەتەوە' : '✅ داخراوە' ?>
            </span>
        </div>

    </main>

    <footer>
        <div style="margin-top:10px; font-size:12px; letter-spacing:1px;">
            &copy; <?= date('Y') ?> &mdash;Group 7
        </div>
    </footer>

    <script>
        // ڕیفرێشکردنی پەڕە هەر 20 چرکە بە ئۆتۆماتیکی
        var seconds = 20;

        var timer = setInterval(function() {
            seconds--;
            if (seconds <= 0) {
                clearInterval(timer);
                location.reload();
            }
        }, 1000);
    </script>

</body>
</html>
