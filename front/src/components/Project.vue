<template>
  <div class="kanban-board">
    <h2 class="kanban-title">Tableau Kanban</h2>

    <div class="kanban-columns">
      <!-- Colonnes du Kanban -->
      <div
        v-for="column in columns"
        :key="column.status"
        class="kanban-column"
        @drop="onDrop($event, column.status)"
        @dragover.prevent
      >
        <h3 class="column-title">{{ column.title }}</h3>

        <!-- Liste des tâches -->
        <div class="tasks-container">
          <div
            v-for="task in getTasksByStatus(column.status)"
            :key="task.id"
            class="kanban-task"
            draggable="true"
            @dragstart="onDragStart($event, task)"
          >
            <div class="task-header">
              <h4>{{ task.title }}</h4>
              <span class="task-priority" :class="getPriorityClass(task.priority)">{{ task.priority }}</span>
            </div>
            <p class="task-description">{{ task.description }}</p>
            <div class="task-footer">
              <span class="task-due-date" v-if="task.due_date">📅 {{ formatDate(task.due_date) }}</span>
            </div>
          </div>

          <!-- Ajouter une nouvelle tâche -->
          <div class="add-task" @click="openTaskModal(column.status)">
            + Ajouter une tâche
          </div>
        </div>
      </div>
    </div>

    <!-- Modal pour ajouter/éditer une tâche -->
    <div v-if="showTaskModal" class="modal-overlay" @click.self="closeTaskModal">
      <div class="modal-content">
        <h3>{{ editingTask ? 'Modifier la tâche' : 'Ajouter une tâche' }}</h3>

        <form @submit.prevent="saveTask">
          <div class="form-group">
            <label for="task-title">Titre</label>
            <input type="text" id="task-title" v-model="currentTask.title" required>
          </div>

          <div class="form-group">
            <label for="task-description">Description</label>
            <textarea id="task-description" v-model="currentTask.description" rows="3"></textarea>
          </div>

          <div class="form-group">
            <label for="task-due-date">Date limite</label>
            <input type="date" id="task-due-date" v-model="currentTask.due_date">
          </div>

          <div class="form-group">
            <label for="task-priority">Priorité</label>
            <select id="task-priority" v-model="currentTask.priority" required>
              <option value="basse">Basse</option>
              <option value="moyenne">Moyenne</option>
              <option value="haute">Haute</option>
              <option value="critique">Critique</option>
            </select>
          </div>

          <div class="modal-actions">
            <button type="button" class="cancel-button" @click="closeTaskModal">Annuler</button>
            <button type="submit" class="save-button">{{ editingTask ? 'Mettre à jour' : 'Ajouter' }}</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import {useRoute} from "vue-router";

// Définition des colonnes du Kanban
const columns = ref([
  { status: 'todo', title: 'À faire' },
  { status: 'en cours', title: 'En cours' },
  { status: 'terminé', title: 'Terminé' }
]);

// Liste des tâches
const tasks = ref([]);

// État du modal
const showTaskModal = ref(false);
const currentTask = ref({
  id: null,
  title: '',
  description: '',
  due_date: '',
  priority: 'moyenne',
  status: 'todo',
  project_id: 2 // À adapter selon ton backend
});
const editingTask = ref(false);
const route = useRoute();
const projectId = ref(route.params.id);
// Récupérer les tâches depuis le backend
const fetchTasks = async () => {
  try {
    const response = await axios.get(`http://localhost:8000/projects/${projectId.value}/tasks`);
    tasks.value = response.data;
  } catch (error) {
    console.error("Erreur lors de la récupération des tâches:", error);
  }
};

// Filtrer les tâches par statut
const getTasksByStatus = (status) => {
  return tasks.value.filter(task => task.status === status);
};

// Formater la date
const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('fr-FR');
};

// Classe CSS selon la priorité
const getPriorityClass = (priority) => {
  return {
    'priority-low': priority === 'basse',
    'priority-medium': priority === 'moyenne',
    'priority-high': priority === 'haute',
    'priority-critical': priority === 'critique'
  };
};

// Ouvrir le modal pour ajouter une tâche
const openTaskModal = (status) => {
  currentTask.value = {
    id: null,
    title: '',
    description: '',
    due_date: '',
    priority: 'moyenne',
    status: status,
    project_id: 1
  };
  editingTask.value = false;
  showTaskModal.value = true;
};

// Fermer le modal
const closeTaskModal = () => {
  showTaskModal.value = false;
};

// Sauvegarder une tâche (création ou mise à jour)
const saveTask = async () => {
  try {
    if (editingTask.value) {
      // Mise à jour d'une tâche existante
      await axios.put(`http://localhost:8000/tasks/${currentTask.value.id}`, currentTask.value);
    } else {
      // Création d'une nouvelle tâche
      const response = await axios.post('http://localhost:8000/tasks', currentTask.value);
      tasks.value.push(response.data);
    }
    await fetchTasks(); // Rafraîchir la liste des tâches
    closeTaskModal();
  } catch (error) {
    console.error("Erreur lors de la sauvegarde de la tâche:", error);
  }
};

// Glisser-déposer : Début du glissement
const onDragStart = (event, task) => {
  event.dataTransfer.setData('taskId', task.id);
};

// Glisser-déposer : Déposer une tâche
const onDrop = async (event, newStatus) => {
  const taskId = event.dataTransfer.getData('taskId');
  const task = tasks.value.find(t => t.id == taskId);

  if (task) {
    try {
      // Mettre à jour le statut de la tâche dans le backend
      await axios.patch(`http://localhost:8000/tasks/${taskId}`, {
        status: newStatus
      });
      // Mettre à jour localement
      task.status = newStatus;
    } catch (error) {
      console.error("Erreur lors du déplacement de la tâche:", error);
    }
  }
};

// Charger les tâches au démarrage
onMounted(fetchTasks);
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600&display=swap');

.kanban-board {
  font-family: 'Poppins', sans-serif;
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.kanban-title {
  text-align: center;
  margin-bottom: 30px;
  color: #2f4f4f;
  font-size: 24px;
  font-weight: 600;
}

.kanban-columns {
  display: flex;
  gap: 20px;
  overflow-x: auto;
}

.kanban-column {
  flex: 1;
  min-width: 300px;
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.column-title {
  margin-bottom: 15px;
  color: #2f4f4f;
  font-size: 18px;
  font-weight: 600;
  text-align: center;
  padding-bottom: 10px;
  border-bottom: 1px solid #e9ecef;
}

.tasks-container {
  min-height: 100px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.kanban-task {
  background-color: white;
  border-radius: 6px;
  padding: 15px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  cursor: grab;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.kanban-task:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.kanban-task:active {
  cursor: grabbing;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.task-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
  color: #2f4f4f;
}

.task-description {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #495057;
  white-space: pre-line;
}

.task-footer {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #6c757d;
}

.task-priority {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.priority-low {
  background-color: #d4edda;
  color: #155724;
}

.priority-medium {
  background-color: #fff3cd;
  color: #856404;
}

.priority-high {
  background-color: #ffeeba;
  color: #856404;
}

.priority-critical {
  background-color: #f8d7da;
  color: #721c24;
}

.task-due-date {
  font-size: 12px;
}

.add-task {
  background-color: #e9ecef;
  border-radius: 6px;
  padding: 10px;
  text-align: center;
  color: #6c757d;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.add-task:hover {
  background-color: #dee2e6;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  padding: 25px;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.modal-content h3 {
  margin-top: 0;
  color: #2f4f4f;
  text-align: center;
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #2f4f4f;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-family: 'Poppins', sans-serif;
  font-size: 14px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.cancel-button {
  padding: 8px 16px;
  background-color: #f8f9fa;
  border: 1px solid #ced4da;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.cancel-button:hover {
  background-color: #e9ecef;
}

.save-button {
  padding: 8px 16px;
  background-color: #047857;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.save-button:hover {
  background-color: #065f46;
}
</style>
