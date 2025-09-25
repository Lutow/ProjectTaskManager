<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <h3>{{ editing ? 'Modifier la tâche' : 'Ajouter une tâche' }}</h3>

      <form @submit.prevent="onSave">
        <div class="form-group">
          <label for="task-title">Titre</label>
          <input type="text" id="task-title" v-model="localTask.title" required />
        </div>

        <div class="form-group">
          <label>Utilisateurs assignés</label>
          <div v-for="user in users" :key="user.id" class="checkbox-item">
            <input
              type="checkbox"
              :id="'user-' + user.id"
              :value="user.id"
              v-model="localTask.user_ids"
            />
            <label :for="'user-' + user.id">{{ user.name }}</label>
          </div>
        </div>

        <div class="form-group">
          <label for="task-description">Description</label>
          <textarea id="task-description" v-model="localTask.description" rows="3"></textarea>
        </div>

        <div class="form-group">
          <label for="task-due-date">Date limite</label>
          <input type="date" id="task-due-date" v-model="localTask.due_date" />
        </div>

        <div class="form-group">
          <label for="task-priority">Priorité</label>
          <select id="task-priority" v-model="localTask.priority" required>
            <option value="basse">Basse</option>
            <option value="moyenne">Moyenne</option>
            <option value="haute">Haute</option>
            <option value="critique">Critique</option>
          </select>
        </div>

        <div class="modal-actions">
          <button type="button" class="cancel-button" @click="$emit('close')">Annuler</button>
          <button type="submit" class="save-button">
            {{ editing ? 'Mettre à jour' : 'Ajouter' }}
          </button>
          <button type="button" class="delete-button" @click="onDelete">Supprimer</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import axios from 'axios'

const props = defineProps({
  task: { type: Object, required: true },
  editing: { type: Boolean, default: false }
})
const emit = defineEmits(['save', 'close', 'delete'])

const localTask = ref({ ...props.task })
const users = ref([]) // List of all users

// Load all users when modal opens
const fetchUsers = async () => {
  try {
    const response = await axios.get('http://localhost:8000/users')
    users.value = response.data
  } catch (error) {
    console.error("Erreur lors du chargement des utilisateurs:", error)
  }
}

onMounted(fetchUsers)

// Sync task prop when modal is opened
watch(
  () => props.task,
  (newTask) => {
    localTask.value = {
      ...newTask,
      user_ids: [...(newTask.user_ids || [])], // keep assigned users
    }
  },
  { immediate: true }
)

// Emit save event
const onSave = () => {
  localTask.value.user_ids = (localTask.value.user_ids || []).map(Number)
  emit('save', localTask.value)
}

// Emit delete event
const onDelete = () => {
  emit('delete', localTask.value.id)
}
</script>


<style scoped>
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

.delete-button {
  padding: 8px 16px;
  background-color: rgba(197, 28, 28, 0.9);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.delete-button:hover {
  background-color: rgba(145, 10, 10, 0.9);
}

.save-button:hover {
  background-color: #065f46;
}
</style>
