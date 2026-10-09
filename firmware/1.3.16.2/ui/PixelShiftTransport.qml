// 自写私有体验版传输；只访问机内 loopback 的固定路由，不发送拍摄命令。
import QtQml
QtObject {
    id: root
    readonly property bool asynchronousControl: true
    property bool connected: false
    property bool experimentalReady: false
    property bool confirmedArmed: false
    property bool busy: false
    property bool settled: false
    property bool cancelEnabled: false
    property bool recovery: false
    property string jobToken: "0"
    property string generationToken: "0"
    property string lastError: ""
    property bool commandPending: false
    property bool inFlight: false
    property bool currentIsCommand: false
    property int confirmedDelay: 2
    property bool confirmedKeep: false
    property bool savedSuccessfully: false
    property bool cancelledSuccessfully: false
    property bool cleanupAfterSave: false
    property string phase: "idle"
    property bool captureVerified: false
    property int delayRemaining: 0
    readonly property bool initialDelayActive: busy && connected && !recovery && phase === "delay" && delayRemaining > 0
    readonly property string progressText: !connected ? "连接中断\n正在核对任务，请勿关机" :
        recovery ? "处理未完成\n请保持供电，勿拔存储卡" :
        initialDelayActive ? "拍摄倒计时 " + delayRemaining + " 秒" :
        phase === "merge" ? "正在合成" : phase === "encode" ? "正在生成成片" :
        phase === "save" ? "正在保存" : phase === "album" ? "正在登记相册" :
        phase === "cleanup" ? "正在清理原片" : "正在采集"
    property int pollTicks: 0
    property var currentRequest: null
    signal commandFinished(bool ok)
    function acceptState(s) {
        if (s.schema !== 1 || typeof s.armed !== "boolean" || typeof s.busy !== "boolean"
                || typeof s.settled !== "boolean" || typeof s.experimentalReady !== "boolean"
                || typeof s.jobToken !== "string" || typeof s.generationToken !== "string"
                || !/^[0-9]{1,18}$/.test(s.jobToken) || !/^[1-9][0-9]{0,17}$/.test(s.generationToken))
            return false
        connected = true
        jobToken = s.jobToken
        generationToken = s.generationToken
        phase = typeof s.phase === "string" ? s.phase : "unknown"
        delayRemaining = typeof s.delayRemaining === "number" && isFinite(s.delayRemaining)
            && s.delayRemaining >= 0 && s.delayRemaining <= 60
            && Math.floor(s.delayRemaining) === s.delayRemaining ? s.delayRemaining : 0
        captureVerified = s.captureVerified === true
        recovery = s.recovery === true
        confirmedArmed = s.armed
        confirmedDelay = typeof s.initialDelay === "number" ? s.initialDelay : -1
        confirmedKeep = s.keepMode === true
        cleanupAfterSave = s.cleanupAfterSave === true
        savedSuccessfully = s.error === "SAVED_DEFAULT_FOLDER_SIX_DELETED"
        cancelledSuccessfully = s.error === "CANCELLED_INPUTS_RETAINED"
            || s.error === "SAVED_999HASBL_INPUTS_RETAINED" || s.error === "SAVED_999HASBL_SIX_DELETED"
        settled = s.settled
        busy = s.busy
        cancelEnabled = s.cancelEnabled === true
        experimentalReady = s.experimentalReady && !recovery
        if (s.error === "CANCELLED_INPUTS_RETAINED") lastError = "已取消，本次原片保留"
        else if (s.error === "SAVED_DEFAULT_FOLDER_SIX_DELETED") lastError = "成片已保存至本次拍摄默认文件夹；本次六张原片已清理"
        else if (s.error === "SAVED_999HASBL_SIX_DELETED") lastError = "成片已保存至 999HASBL；本次六张原片已清理"
        else if (s.error === "SAVED_999HASBL_INPUTS_RETAINED") lastError = "成片已保存至 999HASBL；体验版保留六张原片"
        else if (s.error === "FAST_CAPTURE_GUARD_UNCONFIRMED") lastError = "快门保护未确认，未启用像素超频；请先选择单张拍摄"
        else if (s.error && s.recovery === true) lastError = "任务需核对：" + s.error
        else if (s.error) lastError = "模式未就绪：" + s.error
        else lastError = ""
        return true
    }
    function exchange(method, path) {
        if (inFlight) {
            if (method !== "POST" || currentIsCommand) return false
            var old = currentRequest
            currentRequest = null
            inFlight = false
            if (old) old.abort()
        }
        inFlight = true
        pollTicks = 0
        var command = method === "POST"
        currentIsCommand = command
        if (command) commandPending = true
        var request = new XMLHttpRequest()
        currentRequest = request
        request.onreadystatechange = function () {
            if (request.readyState !== XMLHttpRequest.DONE || root.currentRequest !== request) return
            var ok = false
            try { ok = root.acceptState(JSON.parse(request.responseText)) && request.status === 200 }
            catch (error) { root.connected = false; root.experimentalReady = false }
            root.currentRequest = null
            root.inFlight = false
            if (command) {
                root.commandPending = false
                if (!ok) root.lastError = "操作未获确认；请保留电源和存储卡"
                root.commandFinished(ok)
            }
        }
        request.open(method, "http://127.0.0.1:38408" + path)
        if (command) request.setRequestHeader("X-PixelShift-Local", "1")
        request.send()
        return true
    }
    function arm(delay, keep) {
        if (!connected || !experimentalReady || busy || commandPending) return false
        return exchange("POST", "/arm?delay=" + delay + "&keep=" + (keep ? 1 : 0))
    }
    function disarm() {
        if (!connected || busy || recovery || commandPending) return false
        return exchange("POST", "/disarm")
    }
    function updateOptions(delay, keep) {
        if (!connected || !confirmedArmed || busy || recovery || commandPending) return false
        return exchange("POST", "/options?delay=" + delay + "&keep=" + (keep ? 1 : 0))
    }
    function cancel(job, generation) {
        if (!connected || !busy || !cancelEnabled || job !== jobToken || generation !== generationToken) return false
        return exchange("POST", "/cancel")
    }
    property Timer polling: Timer {
        interval: 300; running: true; repeat: true
        onTriggered: {
            if (!root.inFlight) root.exchange("GET", "/status")
            else if (++root.pollTicks > 50) {
                var request = root.currentRequest
                root.currentRequest = null
                root.inFlight = false
                root.connected = false
                root.experimentalReady = false
                root.commandPending = false
                if (request) request.abort()
                root.lastError = "连接中断，未确认任务结束"
                root.commandFinished(false)
            }
        }
    }
}
