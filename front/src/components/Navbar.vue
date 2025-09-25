<template>
  <nav class="navbar">
    <div class="container">
      <div class="logo">
        <router-link to="/">TaskManager</router-link>
      </div>
      <ul class="nav-links">
        <li><router-link to="/projects">Projects</router-link></li>
        <li v-if="!isAuthenticated">
          <router-link to="/login">Log in / Register</router-link>
        </li>
        <li v-if="isAuthenticated">
          <button @click="handleLogout" class="logout-btn">Disconnect</button>
        </li>
      </ul>
    </div>
  </nav>
  <div v-if="showProfile">
  </div>

</template>


<script>
export default {
  name: 'Navbar',
  components: {
  },
  data() {
    return {
      showProfile: false,
      isAuthenticated: false,
    };
  },
  created() {
    this.checkAuthentication();
    window.addEventListener("storage", this.checkAuthentication);
  },
  methods: {
    checkAuthentication() {
      const token = localStorage.getItem('token');
      this.isAuthenticated = !!token;
    },
    toggleProfile() {
      this.showProfile = !this.showProfile;
    },
    handleLogout() {
      localStorage.removeItem('token');
      localStorage.removeItem('userEmail');
      this.isAuthenticated = false;
      this.$router.push('/');
      setTimeout(() => {
        window.location.reload();
      }, 100)
    },
  },
};
</script>



<style scoped>

.navbar {
  background-color: #e39429;
  color: white;
  padding: 1rem 0;
  font-family: 'Poppins', sans-serif;
}

.navbar a {
  text-decoration: none;
}

.container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1100px;
  margin: auto;
  padding: 0 1.5rem;
}

.logo {
  display: flex;
  align-items: center;
  font-size: 1.5rem;
  font-weight: bold;
  text-decoration: none;
}

.logo a {
  text-decoration: none;
}

.logo a:hover {
  text-decoration: none;
}

.logo a,
.logo a:visited,
.logo a:hover,
.logo a:active,
.logo a:focus {
  color: white !important;
  text-decoration: none !important;
}


.logo span {
  margin-left: 0.4rem;
}

.nav-links {
  padding: 0;
  margin: 0;
  align-items: center;
  list-style: none;
  display: flex;
  gap: 5rem;
}

.nav-links a {
  color: white;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s;
}

.profile-btn {
  background-color: transparent;
  border: 2px solid white;
  color: white;
  padding: 8px 16px;
  cursor: pointer;
  font-weight: 500;
  border-radius: 5px;
  transition: background-color 0.3s, color 0.3s;
}

.profile-btn:hover {
  background-color: white;
  color: #e39429;
}

.logout-btn {
  background-color: red;
  border: none;
  color: white;
  padding: 8px 16px;
  cursor: pointer;
  font-weight: 500;
  border-radius: 5px;
  transition: background-color 0.3s;
}

.logout-btn:hover {
  background-color: darkred;
}

</style>
