<template>
    <div class="center">
        <img src="@/assets/logo.png" id="tinycheck-logo" />
        <div class="loading loading-lg loadingsplash"></div>
    </div>
</template>

<script>
    import router from '../router'
    import axios from 'axios'

    export default {
        name: 'splash-screen',
        components: {},
        data() {
            return {
                internet: false
            }
        },
        methods: {
            internet_check: function() {
                axios.get('/api/network/status', { timeout: 30000 })
                    .then(response => {
                        if (response.data.internet) {
                            this.internet = true
                            setTimeout(function () { this.goto_home(); }.bind(this), 1000);
                        }
                    })
                    .catch(err => (console.log(err)))
            },
            delete_captures: function() {
                axios.get('/api/misc/delete-captures', { timeout: 30000 })
                    .catch(err => (console.log(err)))
            }, 
            goto_home: function() {
                var internet   = this.internet
                router.replace({ name: 'home', params: { internet: internet } });
            }
        },
        created: function() {
            this.delete_captures();
            setTimeout(function () { this.internet_check(); }.bind(this), 5000);
        }
    }
</script>
