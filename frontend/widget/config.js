/**
 * Aidemy Chat Widget Configuration
 */

const AidemyChatConfig = {
    // n8n webhook URL
    webhookUrl: 'https://n8n.jacoposabbacapetta.it/webhook/chat',

    // Widget appearance
    primaryColor: '#4A90E2',
    position: 'bottom-right', // 'bottom-right' or 'bottom-left'

    // Welcome message
    welcomeMessage: `Ciao! Sono Demy, l'assistente di Aidemy.

Mi occupo di aiutare le organizzazioni a navigare il cambiamento attraverso AI generativa, strategia e innovazione. Come posso esserti utile oggi?`,

    // Quick replies (shown on first load)
    quickReplies: [
        'Come funzionano i vostri servizi?',
        'Quali sono i costi indicativi?',
        'Voglio prenotare una call',
        'Avete case study?'
    ],

    // Timeouts
    typingDelay: 1000, // ms to show typing indicator
    requestTimeout: 30000, // 30 seconds

    // Storage
    sessionStorageKey: 'aidemy_chat_session',
    conversationStorageKey: 'aidemy_chat_history',

    // Error messages
    errorMessage: 'Mi dispiace, sto avendo un problema tecnico momentaneo. Riprova tra pochi secondi.',

    // Enable debug mode
    debug: false
};
