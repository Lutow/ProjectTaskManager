<template>
  <div class="kanban-board">
    <h2 class="kanban-title">Tableau Kanban</h2>

    <!-- Stats -->
    <div class="kanban-stats">
      <div class="stat">
        <span class="stat-number">{{ tasks.length }}</span>
        <span class="stat-label">  Tâches totales</span>
      </div>
      <div class="stat" v-for="column in columns" :key="column.status">
        <span class="stat-number">{{ getTasksByStatus(column.status).length }}</span>
        <span class="stat-label">{{ ' ' + column.title }}</span>
      </div>
    </div>
    <br>

    <!-- Colonnes -->
    <div class="kanban-columns">
      <div
        v-for="column in columns"
        :key="column.status"
        class="kanban-column"
        @dragover.prevent
        @drop="onDrop($event, column.status)"
      >
        <h3 class="column-title">{{ column.title }}</h3>

        <div class="tasks-container">
          <KanbanTask
            v-for="task in getTasksByStatus(column.status)"
            :key="task.id"
            :task="task"
            @dragstart="onDragStart"
            @edit="openEditTaskModal"
          />

          <!-- Add Task Button -->
          <div class="add-task" @click="openTaskModal(column.status)">
            + Ajouter une tâche
          </div>
        </div>
      </div>
    </div>

    <TaskModal
      v-if="showTaskModal"
      :task="currentTask"
      :editing="editingTask"
      @close="closeTaskModal"
      @save="saveTask"
      @delete="deletingTask"
    />
  </div>
</template>


<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import axios from 'axios';

import KanbanTask from './KanbanTask.vue';
import TaskModal from './TaskModal.vue';

// Columns definition
const columns = ref([
  { status: 'todo', title: 'À faire' },
  { status: 'en cours', title: 'En cours' },
  { status: 'terminé', title: 'Terminé' }
]);

// Data
const tasks = ref([]);
const showTaskModal = ref(false);
const currentTask = ref({});
const editingTask = ref(false);

const route = useRoute();
const projectId = ref(route.params.id);

// Fetch tasks for this project
const fetchTasks = async () => {
  try {
    const response = await axios.get(`http://localhost:8000/projects/${projectId.value}/tasks`);
    console.log("Réponse backend :", response.data);
    tasks.value = response.data.map(task => ({
      ...task,
      user_ids: task.users ? task.users.map(u => u.id) : [],
    }));
  } catch (error) {
    console.error("Erreur lors de la récupération des tâches:", error);
  }
};

const getTasksByStatus = (status) => {
  return tasks.value.filter(task => task.status === status);
};

// Open modal for add/edit
const openTaskModal = (status) => {
  currentTask.value = {
    title: '',
    participants: [],
    description: '',
    due_date: '',
    priority: 'moyenne',
    status: status,
    project_id: projectId.value
  };
  editingTask.value = false;
  showTaskModal.value = true;
};

const closeTaskModal = () => {
  showTaskModal.value = false;
};

const openEditTaskModal = (task) => {
  currentTask.value = { ...task };
  editingTask.value = true;
  showTaskModal.value = true;
};


const saveTask = async (task) => {
  try {
    let taskId;
    let savedTask;

    if (editingTask.value) {
      // Update
      const response = await axios.put(`http://localhost:8000/tasks/${task.id}`, {
        title: task.title,
        description: task.description || null,
        due_date: task.due_date || null,
        status: task.status,
        priority: task.priority,
        project_id: task.project_id,
      });
      savedTask = response.data;
      taskId = savedTask.id;
    } else {
      // Create
      const response = await axios.post('http://localhost:8000/tasks', {
        title: task.title,
        description: task.description || null,
        due_date: task.due_date || null,
        status: task.status,
        priority: task.priority,
        project_id: task.project_id,
      });
      savedTask = response.data;
      taskId = savedTask.id;
    }

    // Mettre à jour les users assignés si besoin
    if (task.user_ids && task.user_ids.length > 0) {
      await axios.post(`http://localhost:8000/tasks/${taskId}/assign-users`, {
        user_ids: task.user_ids,
      });
    }

    await fetchTasks();

    currentTask.value = { ...savedTask };
    editingTask.value = true;
    showTaskModal.value = false;

  } catch (error) {
    console.error("Erreur lors de la sauvegarde de la tâche:", error);
  }
};



const deletingTask = async (taskId) => {
  try {
    await axios.delete(`http://localhost:8000/tasks/${taskId}`);
    await fetchTasks(); // refresh tasks after deletion
    closeTaskModal();
  } catch (error) {
    console.error("Erreur lors de la suppression de la tâche:", error);
  }
};


// Drag and Drop
const onDragStart = (event, task) => {
  event.dataTransfer.setData('taskId', task.id);
};

const onDrop = async (event, newStatus) => {
  const taskId = event.dataTransfer.getData('taskId');
  console.log("Dragged taskId:", taskId, "newStatus:", newStatus);
  const task = tasks.value.find(t => t.id === Number(taskId));

  if (task) {
    try {
      await axios.put(`http://localhost:8000/tasks/${taskId}`, {
        title: task.title,
        description: task.description,
        due_date: task.due_date,
        priority: task.priority,
        status: newStatus,
      });
      task.status = newStatus;
    } catch (error) {
      console.error("Erreur lors du déplacement de la tâche:", error);
    }
  }
};
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

/* Stats section */
.kanban-stats {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-bottom: 25px;
}

.stat {
  background-color: #f8f9fa;
  padding: 10px 15px;
  border-radius: 6px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.stat-number {
  font-weight: 600;
  font-size: 18px;
  color: #047857;
  display: block;
}

.stat-label {
  font-size: 12px;
  color: #555;
  display: block;
}

</style>
