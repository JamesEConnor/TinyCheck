<template>
    <div class="center">
        <h3 class="lobster">{{ $t("home.welcome_msg") }}<sup>{{current_version}}</sup></h3>
        <p>{{ $t("home.help_msg") }}</p>
        <button class="btn btn-primary" v-on:click="next()">{{ $t("home.start_btn") }}</button>
    </div>
</template>

<script>
import router from '../router'

export default {
    name: 'home',
    props: { internet: Boolean },
     data() {
        return {
            current_version:"" 
        }
    },
    methods: {
        next: function() {
            //TODO: Remove SSID stuff, instead when a user clicks "next"
            //it should go to the screen that generates a user session
            //(including a unique port, session ID, and QR code)
            router.push({ name: 'generate-proxy' });
        }
    },
    created: function() {
        if ('current_version' in window)
            this.current_version = window.current_version
    }
}
</script>
