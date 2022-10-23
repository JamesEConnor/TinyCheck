<!-- TODO: Change this from generating APs to generating Proxies -->

<template>
    <div class="center">
        <div v-if="(error == false)">
            <div v-if="proxy_ip">
                <div class="card apcard" v-on:click="generate_proxy()">
                    <div class="columns">
                        <div class="column col-5"><br />
                            <span class="light-grey">{{ $t("generate-ap.proxy_ip") }} </span><br />
                            <h4>{{ proxy_ip }}</h4>
                            <span class="light-grey">{{ $t("generate-ap.proxy_port") }} </span><br />
                            <h4>{{ proxy_port }}</h4>
                        </div>
                    </div>
                </div>
                <br /><br /><br /><br /> <br /><br /><br /><br /><br /><br />
                <!-- Requite a CSS MEME for that shit :) -->
                <span class="legend">{{ $t("generate-proxy.tap_msg") }}</span>
            </div>
            <div v-else>
                <img src="@/assets/loading.svg"/>
                <p class="legend">{{ $t("generate-proxy.generate_proxy_msg") }}</p>
            </div>
        </div>
        <div v-else>
            <p>
                <strong v-html="$t('generate-proxy.error_msg1')"></strong>
                <br /><br />
            </p>
        </div>
    </div>
    
</template>

<script>
import axios from 'axios'
import router from '../router'

export default {
    name: 'generate-proxy',
    components: {},
    data() {
        return {
            proxy_ip: false,
            proxy_port: false,
            capture_token: false,
            capture_start: false,
            interval: false,
            error: false,
            reboot_option: window.config.reboot_option,
            attempts: 3
        }
    },
    methods: {
        generate_proxy: function() {
            clearInterval(this.interval);
            this.ssid_name = false
            axios.get('/api/network/ap/start', { timeout: 30000 })
                .then(response => (this.show_ap(response.data)))
        },
        show_ap: function(data) {
            if (data.status) {
                this.proxy_ip = data.proxy_ip
                this.proxy_port = data.proxy_port
                this.start_capture() // Start the capture before client connect.
            } else {
                if(this.attempts != 0){
                    setTimeout(function () { this.generate_proxy() }.bind(this), 10000)
                    this.attempts -= 1;
                } else {
                    this.error = true
                }
            }
        },
        start_capture: function() {
            axios.get('/api/capture/start', { timeout: 30000 })
                .then(response => (this.get_capture_token(response.data)))
        },
        reboot: function() {
            axios.get('/api/misc/reboot', { timeout: 30000 })
                .then(response => { console.log(response)})
        },
        get_capture_token: function(data) {
            if (data.status) {
                this.capture_token = data.capture_token
                this.capture_start = Date.now()
                this.get_device()
            }
        },
        get_device: function() {
            this.interval = setInterval(() => {
                axios.get(`/api/device/get/${this.capture_token}`, { timeout: 30000 })
                    .then(response => (this.check_device(response.data)))
            }, 500);
        },
        check_device: function(data) {
            if (data.status) {
                clearInterval(this.interval);
                var capture_token = this.capture_token
                var capture_start = this.capture_start
                var device_name = data.name
                router.replace({
                    name: 'capture',
                    params: {
                        capture_token: capture_token,
                        capture_start: capture_start,
                        device_name: device_name
                    }
                });
            }
        }
    },
    created: function() {
        this.generate_proxy();
    }
}
</script>

