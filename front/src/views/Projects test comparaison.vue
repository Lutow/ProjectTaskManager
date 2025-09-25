<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";
import {useRouter} from "vue-router";

const projects = ref([]); // Variable réactive pour stocker les projets
const isAuthenticated = ref(false);

const checkAuthentication = () => {
  const token = localStorage.getItem('userToken')
  isAuthenticated.value = !!token
}
const fetchProjects = async () => {
  try {
    const response = await axios.get("http://localhost:8000/projects");
    projects.value = response.data; // Stocke les projets dans la variable réactive
    console.log("Projets récupérés :", projects.value);
  } catch (error) {
    console.error("Erreur lors de la récupération des projets :", error.response?.data || error.message);
  }
};

// Appel de la fonction au chargement du composant
onMounted(() => {
  checkAuthentication()
  window.addEventListener('storage', checkAuthentication)
  fetchProjects();
});

const router = useRouter()

const redirect = (project_id) => {
  router.push(`/projects/${project_id}`);
}
</script>

<template>
  <div class="project-header">
    <h2>Mes Projets</h2>
    <button class="cssbuttons-io-button">
      <svg
        height="24"
        width="24"
        viewBox="0 0 24 24"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path d="M0 0h24v24H0z" fill="none"></path>
        <path d="M11 11V5h2v6h6v2h-6v6h-2v-6H5v-2z" fill="currentColor"></path>
      </svg>
      <span>Nouveau</span>
    </button>
  </div>

  <div class="projects-container">
    <!-- Affichage des projets -->
    <div v-if="projects.length > 0" class="projects-grid">
      <div v-for="project in projects" :key="project.id" class="project-card" @click="redirect(project.id)">
        <h3>{{ project.name }}</h3>
        <p>{{ project.description }}</p>
        <p>Statut: {{ project.status }}</p>
        <p>Dates: {{ project.start_date }} - {{ project.end_date }}</p>
      </div>
    </div>
    <div v-else>
      <p>Aucun projet trouvé.</p>
    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

html, body {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 20px 15%;
}

.project-header h2 {
  font-family: 'Poppins', sans-serif;
  font-size: 24px;
  font-weight: 600;
  color: #2f4f4f;
}

.cssbuttons-io-button {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-family: 'Poppins', sans-serif;
  font-weight: 500;
  font-size: 16px;
  padding: 0.7em 1.4em 0.7em 1.1em;
  color: white;
  background: #ad5389;
  background: linear-gradient(
    0deg,
    rgb(0, 0, 0) 0%,
    rgb(0, 0, 0) 100%
  );
  border: none;
  border-radius: 4px;
}

.projects-container {
  margin: 20px 15%;
}

.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.project-card {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease;
}

.project-card:hover {
  transform: translateY(-5px);
}

.project-card h3 {
  font-family: 'Poppins', sans-serif;
  font-size: 18px;
  font-weight: 600;
  color: #2f4f4f;
  margin-bottom: 10px;
}

.project-card p {
  font-family: 'Poppins', sans-serif;
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}
</style>
