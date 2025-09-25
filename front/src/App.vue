<script setup>
import { RouterView } from 'vue-router';
import axios from 'axios';
import Navbar from './components/Navbar.vue';

</script>

<template>
  <div id="app">
    <Navbar />
    <RouterView />
  </div>
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
</style>
