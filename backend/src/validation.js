// Vérifie qu'un événement envoyé par le proxy respecte le format commun
// (docs/format-evenement.md). Renvoie la liste des erreurs (vide si tout va bien).

export const MODULES = ['M1', 'M2', 'M3']
export const DETECTEURS = ['regle', 'modele', 'les_deux']
export const ACTIONS = ['bloquer', 'masquer', 'alerter', 'laisser']
export const ETIQUETTES = [
  'non_sensible',
  'identite',
  'finance',
  'sante',
  'secret_technique',
  'donnees_clients',
]
export const STATUTS = ['nouveau', 'en_cours', 'traite', 'faux_positif']

const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i
// Date ISO 8601 en UTC, ex. 2026-11-12T10:42:07Z ou 2026-11-12T10:42:07.123Z
const DATE_UTC = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{1,3})?Z$/

function texte(valeur, max) {
  return typeof valeur === 'string' && valeur.trim() !== '' && valeur.length <= max
}

export function validerEvenement(e) {
  const erreurs = []

  if (e === null || typeof e !== 'object' || Array.isArray(e)) {
    return ["l'événement doit être un objet JSON"]
  }

  if (!UUID.test(e.id ?? '')) erreurs.push('id : UUID obligatoire')
  if (e.requete_id != null && !UUID.test(e.requete_id)) {
    erreurs.push('requete_id : doit être un UUID ou absent')
  }
  if (!DATE_UTC.test(e.date ?? '') || Number.isNaN(Date.parse(e.date))) {
    erreurs.push('date : format ISO 8601 en UTC attendu (ex. 2026-11-12T10:42:07Z)')
  }

  const source = e.source ?? {}
  if (!texte(source.poste, 64)) erreurs.push('source.poste : texte obligatoire (64 car. max)')
  if (!MODULES.includes(source.module)) {
    erreurs.push(`source.module : une valeur parmi ${MODULES.join(', ')}`)
  }

  if (!texte(e.site_ia, 255)) erreurs.push('site_ia : texte obligatoire')
  if (!texte(e.type_donnee, 64)) erreurs.push('type_donnee : texte obligatoire')
  if (!texte(e.regle, 128)) erreurs.push('regle : texte obligatoire')
  if (!DETECTEURS.includes(e.detecteur)) {
    erreurs.push(`detecteur : une valeur parmi ${DETECTEURS.join(', ')}`)
  }
  if (typeof e.score !== 'number' || e.score < 0 || e.score > 1) {
    erreurs.push('score : nombre entre 0 et 1')
  }

  // L'étiquette est obligatoire pour M1, facultative pour les autres modules
  if (e.etiquette != null && !ETIQUETTES.includes(e.etiquette)) {
    erreurs.push(`etiquette : une valeur parmi ${ETIQUETTES.join(', ')}`)
  } else if (e.etiquette == null && source.module === 'M1') {
    erreurs.push('etiquette : obligatoire pour le module M1')
  }

  if (!texte(e.explication, 500)) erreurs.push('explication : texte obligatoire (500 car. max)')
  if (!ACTIONS.includes(e.action)) {
    erreurs.push(`action : une valeur parmi ${ACTIONS.join(', ')}`)
  }
  if (typeof e.extrait_masque !== 'string' || e.extrait_masque.length > 200) {
    erreurs.push('extrait_masque : texte de 200 caractères maximum')
  }
  if (e.version_modele != null && !texte(e.version_modele, 64)) {
    erreurs.push('version_modele : texte (64 car. max) ou null')
  }
  if (
    e.latence_ms != null &&
    (!Number.isInteger(e.latence_ms) || e.latence_ms < 0)
  ) {
    erreurs.push('latence_ms : entier positif ou absent')
  }

  return erreurs
}
