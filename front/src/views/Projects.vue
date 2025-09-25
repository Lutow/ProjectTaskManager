<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";
import ProjectModal from "@/components/ProjectModal.vue";
import { useRouter } from "vue-router";

const projects = ref([]);
const isAuthenticated = ref(false);
const userId = ref(null);
const showProjectModal = ref(false);
const currentProject = ref(null);

const checkAuthentication = () => {
  const token = localStorage.getItem("token");
  isAuthenticated.value = !!token;
};


const authHeaders = () => {
  const token = localStorage.getItem("token");
  return {
    Authorization: `Bearer ${token}`,
  };
};

const fetchProjects = async () => {
  const token = localStorage.getItem("token");
  if (!token) {
    projects.value = [];
    return;
  }

  try {
    const response = await axios.get("http://localhost:8000/my-projects", {
      headers: { Authorization: `Bearer ${token}` },
    });
    projects.value = response.data;
    console.log("Projets récupérés :", projects.value);
    isAuthenticated.value = true;
  } catch (error) {
    console.error("Erreur récupération projets :", error.response?.data || error.message);
    isAuthenticated.value = false;
    projects.value = [];
  }
};




const openProjectModal = (project = null) => {
  if (project) {
    // édition
    currentProject.value = { ...project };
  } else {
    // création : pas d'id
    currentProject.value = {
      name: '',
      description: '',
      start_date: '',
      end_date: '',
      status: 'actif',
    };
  }
  showProjectModal.value = true;
};

const closeProjectModal = () => {
  showProjectModal.value = false;
  currentProject.value = null;
};

const saveProject = async (project) => {
  const token = localStorage.getItem("token");
  if (!token) return;

  try {
    if (project && project.id) {
      await axios.put(`http://localhost:8000/projects/${project.id}`, project, {
        headers: { Authorization: `Bearer ${token}` },
      });
    } else {
      const response = await axios.post("http://localhost:8000/projects", project, {
        headers: { Authorization: `Bearer ${token}` },
      });
      projects.value.push(response.data);
    }
    await fetchProjects();
    closeProjectModal();
  } catch (error) {
    console.error("Erreur sauvegarde projet:", error.response?.data || error.message);
  }
};


const deleteProject = async (projectId) => {
  console.log("Project ID to delete:", projectId, typeof projectId);
  try {
    await axios.delete(`http://localhost:8000/projects/${Number(projectId)}`, {
      headers: authHeaders(),
    });
    projects.value = projects.value.filter((p) => p.id !== Number(projectId));
    closeProjectModal();
  } catch (error) {
    console.error(
      "Erreur suppression projet:",
      error.response?.data || error.message
    );
  }
};

onMounted(() => {
  checkAuthentication();
  window.addEventListener("storage", checkAuthentication);
  fetchProjects();
});

const router = useRouter();

const redirect = (project_id) => {
  router.push(`/projects/${project_id}`);
};
</script>

<template>
  <div class="project-header" v-if="isAuthenticated">
    <h2>Mes Projets</h2>
    <button class="cssbuttons-io-button" @click="openProjectModal()">
      <svg height="24" width="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path d="M0 0h24v24H0z" fill="none"></path>
        <path d="M11 11V5h2v6h6v2h-6v6h-2v-6H5v-2z" fill="currentColor"></path>
      </svg>
      <span>Nouveau</span>
    </button>
  </div>

  <div v-if="isAuthenticated" class="projects-container">
    <div v-if="projects.length > 0" class="projects-grid">
      <div
        v-for="project in projects"
        :key="project.id"
        class="project-card"
        @click="redirect(project.id)"
      >
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <h3>{{ project.name }}</h3>
          <div>
            <button class="edit-btn" @click.stop="openProjectModal(project)">Modifier</button>
            <button class="delete-btn" @click.stop="deleteProject(project.id)">Supprimer</button>
          </div>
        </div>

        <p>{{ project.description }}</p>
        <p>Statut: {{ project.status }}</p>
        <p>Dates: {{ project.start_date }} - {{ project.end_date }}</p>
      </div>
    </div>
    <div v-else>
      <p>Aucun projet trouvé.</p>
    </div>
  </div>

  <div v-else>
    <p>Veuillez vous connecter pour voir vos projets.</p>
  </div>

  <ProjectModal
    v-if="showProjectModal"
    :project="currentProject"
    @save="saveProject"
    @delete="deleteProject"
    @close="closeProjectModal"
  />
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
  font-family: 'Poppins', sans-serif;
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease;
}

.edit-btn {
  padding: 8px 16px;
  background-color: #000000;
  color: white;
  border: none;
  cursor: pointer;
}

.delete-btn {
  padding: 8px 16px;
  margin-left: 20px;
  background-color: #dc2626;
  color: white;
  border: none;
  cursor: pointer;
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
