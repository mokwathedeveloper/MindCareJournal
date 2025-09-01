/**
 * MindCare - Custom Icon Mappings
 * Maps custom icon names to standard Feather icons
 */

const ICON_MAPPINGS = {
  // Custom icon mappings
  'brain': 'activity',           // AI/Intelligence features
  'cookie': 'lock',              // Privacy/Cookie policy
  'shield-check': 'shield',      // Security features

  // Standard icons we commonly use
  'edit': 'edit-2',             // More visible edit icon
  'delete': 'trash-2',          // More visible delete icon
  'save': 'save',               // Save actions
  'cancel': 'x',                // Cancel actions
  'success': 'check-circle',    // Success messages
  'error': 'alert-circle',      // Error messages
  'warning': 'alert-triangle',  // Warning messages
  'info': 'info',               // Info messages
  'settings': 'settings',       // Settings/configuration
  'user': 'user',               // User/profile
  'logout': 'log-out',          // Logout
  'login': 'log-in',            // Login
  'register': 'user-plus',      // Registration
  'mood': 'smile',              // Mood/emotions
  'journal': 'book',            // Journal entries
  'calendar': 'calendar',       // Dates
  'time': 'clock',              // Time
  'trend': 'trending-up',       // Analytics/trends
  'chart': 'bar-chart-2',       // Charts/graphs
  'notification': 'bell',       // Notifications
  'search': 'search',           // Search functionality
  'help': 'help-circle',        // Help/support
  'premium': 'star',            // Premium features
  'home': 'home',               // Home/dashboard
  'menu': 'menu',               // Navigation menu
  'close': 'x',                 // Close/dismiss
  'add': 'plus-circle',         // Add new items
  'remove': 'minus-circle',     // Remove items
  'link': 'link-2',             // External links
  'download': 'download',       // Downloads
  'upload': 'upload',           // Uploads
  'refresh': 'refresh-cw',      // Refresh/reload
  'filter': 'filter',           // Filter options
  'sort': 'chevrons-up-down',   // Sort options
  'expand': 'chevron-down',     // Expand sections
  'collapse': 'chevron-up',     // Collapse sections
  'previous': 'chevron-left',   // Previous page/item
  'next': 'chevron-right',      // Next page/item
  'first': 'chevrons-left',     // First page
  'last': 'chevrons-right'      // Last page
};

// Initialize custom icons
function initializeCustomIcons() {
  // Replace any custom icons with their mapped standard icons
  document.querySelectorAll('[data-feather]').forEach(iconElement => {
    const iconName = iconElement.getAttribute('data-feather');
    if (ICON_MAPPINGS[iconName]) {
      iconElement.setAttribute('data-feather', ICON_MAPPINGS[iconName]);
    }
  });

  // Initialize Feather icons
  if (typeof feather !== 'undefined') {
    feather.replace();
  }
}

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { ICON_MAPPINGS, initializeCustomIcons };
}
