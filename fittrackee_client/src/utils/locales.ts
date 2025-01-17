/* eslint-disable import/no-duplicates */
import { Locale } from 'date-fns'
import { de, enUS, fr } from 'date-fns/locale'

import createI18n from '@/i18n'

export const localeFromLanguage: Record<string, Locale> = {
  de: de,
  en: enUS,
  fr: fr,
  // nb: nb, // disabled for now
}

export const languageLabels: Record<string, string> = {
  de: 'Deutsch',
  en: 'English',
  fr: 'Français',
  // nb: 'Norsk bokmål', // disabled for now
}

const { availableLocales } = createI18n.global
export const availableLanguages = availableLocales.map((l) => {
  return { label: languageLabels[l], value: l }
})
