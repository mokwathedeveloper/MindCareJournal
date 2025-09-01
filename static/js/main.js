/**
 * MindCare - Main JavaScript File
 * Handles general UI interactions, form validation, and common functionality
 *
 * @requires icon-mappings.js - For custom icon handling
 */

document.addEventListener("DOMContentLoaded", function () {
  // Initialize Feather Icons
  // Load custom icon mappings if available
  if (typeof initializeCustomIcons === "function") {
    initializeCustomIcons();
  } else if (typeof feather !== "undefined") {
    feather.replace();
  }

  // Initialize Bootstrap tooltips
  initializeTooltips();

  // Initialize form validation
  initializeFormValidation();

  // Initialize auto-save functionality
  initializeAutoSave();

  // Initialize smooth scrolling
  initializeSmoothScrolling();

  // Initialize keyboard shortcuts
  initializeKeyboardShortcuts();

  // Initialize mood badge interactions
  initializeMoodBadges();

  // Initialize navigation active states
  initializeNavigation();

  // Initialize loading states
  initializeLoadingStates();
});

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
  const tooltipTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="tooltip"]'),
  );
  const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });
}

/**
 * Initialize form validation for all forms with needs-validation class
 */
function initializeFormValidation() {
  const forms = document.getElementsByClassName("needs-validation");

  Array.prototype.filter.call(forms, function (form) {
    form.addEventListener(
      "submit",
      function (event) {
        if (form.checkValidity() === false) {
          event.preventDefault();
          event.stopPropagation();

          // Focus on first invalid field
          const firstInvalidField = form.querySelector(":invalid");
          if (firstInvalidField) {
            firstInvalidField.focus();
          }
        }
        form.classList.add("was-validated");
      },
      false,
    );
  });

  // Real-time validation feedback
  const inputs = document.querySelectorAll(
    ".needs-validation input, .needs-validation textarea",
  );
  inputs.forEach((input) => {
    input.addEventListener("blur", function () {
      if (this.checkValidity()) {
        this.classList.remove("is-invalid");
        this.classList.add("is-valid");
      } else {
        this.classList.remove("is-valid");
        this.classList.add("is-invalid");
      }
    });

    input.addEventListener("input", function () {
      if (this.classList.contains("is-invalid") && this.checkValidity()) {
        this.classList.remove("is-invalid");
        this.classList.add("is-valid");
      }
    });
  });
}

/**
 * Initialize auto-save functionality for forms
 */
function initializeAutoSave() {
  const titleInput = document.getElementById("title");
  const contentTextarea = document.getElementById("content");

  if (titleInput && contentTextarea) {
    let autoSaveTimeout;
    const AUTOSAVE_DELAY = 3000; // 3 seconds
    const DRAFT_KEY = "mindcare_journal_draft";

    // Load existing draft
    loadDraft();

    // Auto-save on input
    [titleInput, contentTextarea].forEach((element) => {
      element.addEventListener("input", function () {
        clearTimeout(autoSaveTimeout);
        autoSaveTimeout = setTimeout(saveDraft, AUTOSAVE_DELAY);

        // Show auto-save indicator
        showAutoSaveIndicator("saving");
      });
    });

    function saveDraft() {
      const title = titleInput.value.trim();
      const content = contentTextarea.value.trim();

      if (title || content) {
        const draft = {
          title: title,
          content: content,
          timestamp: Date.now(),
          url: window.location.pathname,
        };

        localStorage.setItem(DRAFT_KEY, JSON.stringify(draft));
        showAutoSaveIndicator("saved");
      }
    }

    function loadDraft() {
      try {
        const draftData = localStorage.getItem(DRAFT_KEY);
        if (draftData) {
          const draft = JSON.parse(draftData);
          const hoursSinceDraft =
            (Date.now() - draft.timestamp) / (1000 * 60 * 60);

          // Only load draft if it's less than 24 hours old, for the same URL, and fields are empty
          if (
            hoursSinceDraft < 24 &&
            draft.url === window.location.pathname &&
            !titleInput.value &&
            !contentTextarea.value
          ) {
            showDraftRestorePrompt(draft);
          }
        }
      } catch (error) {
        console.warn("Failed to load draft:", error);
      }
    }

    function showDraftRestorePrompt(draft) {
      const restoreModal = createRestoreModal(draft);
      document.body.appendChild(restoreModal);
      const modal = new bootstrap.Modal(restoreModal);
      modal.show();
    }

    function createRestoreModal(draft) {
      const modalHtml = `
                <div class="modal fade" id="restoreDraftModal" tabindex="-1">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">
                                    <i data-feather="save" class="me-2"></i>
                                    Restore Previous Draft?
                                </h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <p>We found a previous draft from ${new Date(draft.timestamp).toLocaleString()}.</p>
                                <div class="card bg-light">
                                    <div class="card-body">
                                        <h6 class="card-title">${draft.title || "Untitled"}</h6>
                                        <p class="card-text">${draft.content.substring(0, 100)}${draft.content.length > 100 ? "..." : ""}</p>
                                    </div>
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Discard</button>
                                <button type="button" class="btn btn-primary" onclick="restoreDraft()">Restore Draft</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;

      const modalElement = document.createElement("div");
      modalElement.innerHTML = modalHtml;

      // Add restore function to global scope temporarily
      window.restoreDraft = function () {
        titleInput.value = draft.title;
        contentTextarea.value = draft.content;
        bootstrap.Modal.getInstance(
          document.getElementById("restoreDraftModal"),
        ).hide();
        delete window.restoreDraft;
        modalElement.remove();

        // Trigger validation
        titleInput.dispatchEvent(new Event("input"));
        contentTextarea.dispatchEvent(new Event("input"));
      };

      return modalElement.firstElementChild;
    }

    function showAutoSaveIndicator(status) {
      let indicator = document.getElementById("autosave-indicator");

      if (!indicator) {
        indicator = document.createElement("div");
        indicator.id = "autosave-indicator";
        indicator.className =
          "position-fixed bottom-0 end-0 m-3 p-2 bg-dark text-white rounded";
        indicator.style.zIndex = "1050";
        indicator.style.opacity = "0";
        indicator.style.transition = "opacity 0.3s ease";
        document.body.appendChild(indicator);
      }

      if (status === "saving") {
        indicator.innerHTML =
          '<i data-feather="save" class="me-1"></i>Saving...';
        indicator.style.opacity = "0.8";
      } else if (status === "saved") {
        indicator.innerHTML = '<i data-feather="check" class="me-1"></i>Saved';
        indicator.style.opacity = "0.8";

        // Replace feather icons
        if (typeof feather !== "undefined") {
          feather.replace();
        }

        setTimeout(() => {
          indicator.style.opacity = "0";
        }, 2000);
      }
    }

    // Clear draft on successful form submission
    const form = titleInput.closest("form");
    if (form) {
      form.addEventListener("submit", function (event) {
        if (form.checkValidity()) {
          localStorage.removeItem(DRAFT_KEY);
        }
      });
    }
  }
}

/**
 * Initialize smooth scrolling for anchor links
 */
function initializeSmoothScrolling() {
  const scrollLinks = document.querySelectorAll('a[href^="#"]');

  scrollLinks.forEach((link) => {
    link.addEventListener("click", function (event) {
      const targetId = this.getAttribute("href").substring(1);
      const targetElement = document.getElementById(targetId);

      if (targetElement) {
        event.preventDefault();
        targetElement.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      }
    });
  });
}

/**
 * Initialize keyboard shortcuts
 */
function initializeKeyboardShortcuts() {
  document.addEventListener("keydown", function (event) {
    // Ctrl/Cmd + Enter to submit forms
    if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
      const activeForm = document.activeElement.closest("form");
      if (activeForm) {
        event.preventDefault();
        const submitButton = activeForm.querySelector('button[type="submit"]');
        if (submitButton) {
          submitButton.click();
        }
      }
    }

    // Ctrl/Cmd + N for new entry (only on dashboard)
    if (
      ((event.ctrlKey || event.metaKey) &&
        event.key === "n" &&
        window.location.pathname === "/") ||
      window.location.pathname === "/dashboard"
    ) {
      event.preventDefault();
      window.location.href = "/new-entry";
    }

    // Escape to close modals
    if (event.key === "Escape") {
      const openModal = document.querySelector(".modal.show");
      if (openModal) {
        const modalInstance = bootstrap.Modal.getInstance(openModal);
        if (modalInstance) {
          modalInstance.hide();
        }
      }
    }
  });
}

/**
 * Initialize mood badge interactions
 */
function initializeMoodBadges() {
  const moodBadges = document.querySelectorAll(".mood-badge");

  moodBadges.forEach((badge) => {
    const moodScore = parseInt(badge.textContent.split("/")[0]);

    // Add tooltip with mood description
    let moodDescription = "";
    switch (moodScore) {
      case 1:
        moodDescription = "Very Low - Feeling quite down or distressed";
        break;
      case 2:
        moodDescription = "Low - Experiencing some negative emotions";
        break;
      case 3:
        moodDescription = "Neutral - Balanced emotional state";
        break;
      case 4:
        moodDescription = "Good - Feeling positive and content";
        break;
      case 5:
        moodDescription = "Excellent - Very happy and optimistic";
        break;
      default:
        moodDescription = "Mood score";
    }

    badge.setAttribute("data-bs-toggle", "tooltip");
    badge.setAttribute("data-bs-placement", "top");
    badge.setAttribute("title", moodDescription);

    // Initialize tooltip
    new bootstrap.Tooltip(badge);

    // Add hover effect
    badge.addEventListener("mouseenter", function () {
      this.style.transform = "scale(1.1)";
      this.style.transition = "transform 0.2s ease";
    });

    badge.addEventListener("mouseleave", function () {
      this.style.transform = "scale(1)";
    });
  });
}

/**
 * Initialize navigation active states
 */
function initializeNavigation() {
  const currentPath = window.location.pathname;
  const navLinks = document.querySelectorAll(".navbar-nav .nav-link");

  navLinks.forEach((link) => {
    const linkPath = new URL(link.href).pathname;

    if (
      linkPath === currentPath ||
      (currentPath.startsWith("/entry") && linkPath === "/dashboard") ||
      (currentPath === "/" && linkPath === "/dashboard")
    ) {
      link.classList.add("active");
    }
  });
}

/**
 * Initialize loading states for buttons and forms
 */
function initializeLoadingStates() {
  const forms = document.querySelectorAll("form");

  forms.forEach((form) => {
    form.addEventListener("submit", function (event) {
      if (form.checkValidity()) {
        const submitButton = form.querySelector('button[type="submit"]');
        if (submitButton) {
          showButtonLoading(submitButton);
        }
      }
    });
  });
}

/**
 * Show loading state on button
 */
function showButtonLoading(button) {
  const originalText = button.innerHTML;
  const loadingText =
    '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Processing...';

  button.innerHTML = loadingText;
  button.disabled = true;

  // Store original text for potential restoration
  button.setAttribute("data-original-text", originalText);
}

/**
 * Restore button from loading state
 */
function restoreButtonFromLoading(button) {
  const originalText = button.getAttribute("data-original-text");
  if (originalText) {
    button.innerHTML = originalText;
    button.disabled = false;
    button.removeAttribute("data-original-text");
  }
}

/**
 * Utility function to format dates
 */
function formatDate(date, options = {}) {
  const defaultOptions = {
    year: "numeric",
    month: "long",
    day: "numeric",
  };

  const formatOptions = { ...defaultOptions, ...options };
  return new Date(date).toLocaleDateString(undefined, formatOptions);
}

/**
 * Utility function to show toast notifications
 */
function showToast(message, type = "info", duration = 3000) {
  const toastContainer = getOrCreateToastContainer();

  const toastHtml = `
        <div class="toast align-items-center text-white bg-${type} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;

  const toastElement = document.createElement("div");
  toastElement.innerHTML = toastHtml;
  const toast = toastElement.firstElementChild;

  toastContainer.appendChild(toast);

  const bsToast = new bootstrap.Toast(toast, { delay: duration });
  bsToast.show();

  // Remove toast element after it's hidden
  toast.addEventListener("hidden.bs.toast", function () {
    toast.remove();
  });
}

/**
 * Get or create toast container
 */
function getOrCreateToastContainer() {
  let container = document.getElementById("toast-container");

  if (!container) {
    container = document.createElement("div");
    container.id = "toast-container";
    container.className = "toast-container position-fixed bottom-0 end-0 p-3";
    container.style.zIndex = "1055";
    document.body.appendChild(container);
  }

  return container;
}

/**
 * Utility function to debounce function calls
 */
function debounce(func, wait, immediate) {
  let timeout;
  return function executedFunction() {
    const context = this;
    const args = arguments;

    const later = function () {
      timeout = null;
      if (!immediate) func.apply(context, args);
    };

    const callNow = immediate && !timeout;
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);

    if (callNow) func.apply(context, args);
  };
}

/**
 * Initialize lazy loading for images
 */
function initializeLazyLoading() {
  if ("IntersectionObserver" in window) {
    const imageObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const img = entry.target;
          img.src = img.dataset.src;
          img.classList.remove("lazy");
          observer.unobserve(img);
        }
      });
    });

    document.querySelectorAll("img[data-src]").forEach((img) => {
      imageObserver.observe(img);
    });
  }
}

/**
 * Initialize accessibility features
 */
function initializeAccessibility() {
  // Add skip to main content link
  const skipLink = document.createElement("a");
  skipLink.href = "#main-content";
  skipLink.textContent = "Skip to main content";
  skipLink.className =
    "visually-hidden-focusable btn btn-primary position-absolute top-0 start-0 m-2";
  skipLink.style.zIndex = "1060";
  document.body.insertBefore(skipLink, document.body.firstChild);

  // Add main content id if not present
  const main = document.querySelector("main");
  if (main && !main.id) {
    main.id = "main-content";
  }

  // Enhance form accessibility
  const forms = document.querySelectorAll("form");
  forms.forEach((form) => {
    const invalidInputs = form.querySelectorAll(":invalid");
    if (invalidInputs.length > 0) {
      form.setAttribute("aria-describedby", "form-errors");

      const errorContainer = document.createElement("div");
      errorContainer.id = "form-errors";
      errorContainer.setAttribute("aria-live", "polite");
      errorContainer.className = "visually-hidden";
      form.appendChild(errorContainer);
    }
  });
}

// Initialize accessibility features when DOM is ready
document.addEventListener("DOMContentLoaded", function () {
  if (typeof initializeAccessibility === "function") {
    initializeAccessibility();
  }
});

// Global error handler
window.addEventListener("error", function (event) {
  console.error(
    "JavaScript error:",
    event.error || event.message || "Unknown error",
  );

  // Show user-friendly error message for critical errors
  if (event.error && event.error.name !== "ChunkLoadError") {
    try {
      if (typeof showToast === "function") {
        showToast(
          "An unexpected error occurred. Please refresh the page.",
          "danger",
          5000,
        );
      } else {
        console.error("showToast function not available");
        // Fallback alert
        alert("An unexpected error occurred. Please refresh the page.");
      }
    } catch (e) {
      console.error("Error in error handler:", e);
    }
  }
});

// Handle network errors
window.addEventListener("online", function () {
  try {
    if (typeof showToast === "function") {
      showToast("Connection restored", "success");
    }
  } catch (e) {
    console.error("Error showing online toast:", e);
  }
});

window.addEventListener("offline", function () {
  try {
    if (typeof showToast === "function") {
      showToast("You are currently offline", "warning", 5000);
    }
  } catch (e) {
    console.error("Error showing offline toast:", e);
  }
});

// Export utility functions for use in other scripts
window.MindCareUtils = {
  showToast,
  formatDate,
  debounce,
  showButtonLoading,
  restoreButtonFromLoading,
};
