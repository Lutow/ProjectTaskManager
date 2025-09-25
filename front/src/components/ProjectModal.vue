<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <h3>{{ isEditing ? 'Modifier le projet' : 'Ajouter un projet' }}</h3>

      <form @submit.prevent="onSave">
        <div class="form-group">
          <label for="project-name">Nom du projet</label>
          <input type="text" id="project-name" v-model="localProject.name" required />
        </div>

        <div class="form-group">
          <label for="project-description">Description</label>
          <textarea id="project-description" v-model="localProject.description" rows="3"></textarea>
        </div>

        <div class="form-group">
          <label for="project-start">Date de début</label>
          <input type="date" id="project-start" v-model="localProject.start_date" />
        </div>

        <div class="form-group">
          <label for="project-end">Date de fin</label>
          <input type="date" id="project-end" v-model="localProject.end_date" />
        </div>

        <div class="form-group">
          <label for="project-status">Statut</label>
          <select id="project-status" v-model="localProject.status" required>
            <option value="actif">Actif</option>
            <option value="archivé">Archivé</option>
          </select>
        </div>

        <div class="modal-actions">
          <button type="button" class="cancel-button" @click="$emit('close')">Annuler</button>
          <button type="submit" class="save-button">{{ isEditing ? 'Mettre à jour' : 'Ajouter' }}</button>
          <button v-if="isEditing" type="button" class="delete-button" @click="onDelete">Supprimer</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'

const props = defineProps({
  project: { type: Object, required: true } // passe toujours un objet
})
const emit = defineEmits(['save', 'close', 'delete'])

const localProject = ref({ ...props.project })

watch(
  () => props.project,
  (newProject) => {
    localProject.value = { ...(newProject || {}) };
  },
  { immediate: true }
)

const isEditing = computed(() => {
  return !!(localProject.value && localProject.value.id);
});

const onSave = () => {
  // envoyer l'objet complet (avec id si édition)
  emit('save', { ...localProject.value });
};

const onDelete = () => {
  if (localProject.value && localProject.value.id) {
    emit('delete', Number(localProject.value.id));
  }
};
</script>


<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

.modal-overlay {
  font-family: 'Poppins', sans-serif;
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}
.modal-content {
  font-family: 'Poppins', sans-serif;
  background-color: white;
  padding: 25px;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}
.form-group { margin-bottom: 15px; }
.form-group label { display: block; margin-bottom: 5px; }
.form-group input,
.form-group textarea,
.form-group select { width: 100%; padding: 10px; border: 1px solid #ced4da; border-radius: 4px; }
.modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px; }
.cancel-button { padding: 8px 16px; border: 1px solid #ced4da; background: #f8f9fa; cursor: pointer; }
.save-button { padding: 8px 16px; background-color: #047857; color: white; border: none; cursor: pointer; }
.delete-button { padding: 8px 16px; background-color: #dc2626; color: white; border: none; cursor: pointer; }
</style>
