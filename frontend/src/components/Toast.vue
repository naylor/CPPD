<template>
    <transition-group name="toast-fade" tag="div" class="toast-container">
        <div v-for="(toast, index) in toasts" :key="toast.id" class="toast" :class="toast.type" role="alert"
            @mouseenter="pauseToast(toast.id)" @mouseleave="resumeToast(toast.id)">
            <span class="toast-message">{{ toast.message }}</span>
            <button class="toast-close" @click="removeToast(toast.id)" aria-label="Fechar">&times;</button>
        </div>
    </transition-group>
</template>

<script>
let toastId = 0;

export default {
    name: "Toast",
    data() {
        return {
            toasts: []
        };
    },
    methods: {
        show({ message, type = "info", duration = 3500 }) {
            toastId += 1;
            const id = toastId;
            const toast = {
                id,
                message,
                type,
                duration,
                timer: null,
                paused: false,
                remaining: duration,
                startTime: null
            };
            this.toasts.push(toast);
            this.startTimer(toast);
            return id;
        },
        startTimer(toast) {
            toast.startTime = Date.now();
            toast.timer = setTimeout(() => {
                this.removeToast(toast.id);
            }, toast.remaining);
        },
        pauseToast(id) {
            const toast = this.toasts.find(t => t.id === id);
            if (toast && toast.timer) {
                clearTimeout(toast.timer);
                toast.timer = null;
                toast.paused = true;
                toast.remaining -= Date.now() - toast.startTime;
            }
        },
        resumeToast(id) {
            const toast = this.toasts.find(t => t.id === id);
            if (toast && !toast.timer && toast.paused) {
                toast.paused = false;
                this.startTimer(toast);
            }
        },
        removeToast(id) {
            const idx = this.toasts.findIndex(t => t.id === id);
            if (idx !== -1) {
                const toast = this.toasts[idx];
                if (toast.timer) clearTimeout(toast.timer);
                this.toasts.splice(idx, 1);
            }
        }
    }
};
</script>

<style scoped>
.toast-container {
    position: fixed;
    top: 24px;
    right: 26px;
    z-index: 9999;
    display: flex;
    flex-direction: column;
    gap: 10px;
    pointer-events: none;
}

.toast {
    min-width: 240px;
    max-width: 340px;
    background: #fff;
    color: #222;
    border-radius: 6px;
    box-shadow: 0 4px 18px #0002;
    padding: 14px 50px 14px 16px;
    font-size: 1.03rem;
    font-weight: 500;
    display: flex;
    align-items: center;
    position: relative;
    pointer-events: auto;
    border-left: 5px solid #0075ff;
    opacity: 0.98;
    transition: background 0.18s, border-color 0.18s;
}

.toast.success {
    border-left-color: #14b714;
    background: #f0fff0;
}

.toast.error {
    border-left-color: #d92424;
    background: #fff4f4;
}

.toast.info {
    border-left-color: #0075ff;
    background: #f5f8ff;
}

.toast.warning {
    border-left-color: #ffa600;
    background: #fffbe8;
}

.toast-message {
    flex: 1;
    margin-right: 8px;
}

.toast-close {
    background: transparent;
    border: none;
    color: #888;
    font-weight: bold;
    font-size: 1.25em;
    cursor: pointer;
    position: absolute;
    top: 6px;
    right: 10px;
    padding: 0 4px;
    outline: none;
    transition: color 0.2s;
    pointer-events: auto;
}

.toast-close:hover {
    color: #c00;
    background: #fff0;
}

.toast-fade-enter-active,
.toast-fade-leave-active {
    transition: all 0.32s cubic-bezier(0.25, 1, 0.5, 1);
}

.toast-fade-enter-from {
    opacity: 0;
    transform: translateY(-20px) scale(0.92);
}

.toast-fade-enter-to {
    opacity: 1;
    transform: translateY(0) scale(1);
}

.toast-fade-leave-from {
    opacity: 1;
    transform: translateY(0) scale(1);
}

.toast-fade-leave-to {
    opacity: 0;
    transform: translateY(-20px) scale(0.92);
}
</style>