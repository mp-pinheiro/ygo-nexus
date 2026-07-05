// Transient status line for blocked actions (forbidden / over-limit / full deck).
let _msg = $state(null)
let _timer

export const toast = {
  get msg() {
    return _msg
  },
}

export function showToast(msg, ms = 1900) {
  _msg = msg
  clearTimeout(_timer)
  _timer = setTimeout(() => (_msg = null), ms)
}
