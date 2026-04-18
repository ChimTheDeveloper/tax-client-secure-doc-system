/**
 * Tax Intelligence System - Phase 3 Utilities
 * Minimal vanilla JavaScript for:
 * - Hamburger menu toggle
 * - Form validation (real-time)
 * - Password strength meter
 * - Progressive enhancement (works without server-side JS)
 */

(function() {
    'use strict';

    // ========================================================
    // Hamburger Menu Toggle
    // ========================================================
    
    function initHamburgerMenu() {
        const hamburger = document.querySelector('.hamburger');
        const mobileNav = document.querySelector('.mobile-nav');
        
        if (!hamburger || !mobileNav) return;
        
        hamburger.addEventListener('click', () => {
            const isExpanded = hamburger.getAttribute('aria-expanded') === 'true';
            hamburger.setAttribute('aria-expanded', !isExpanded);
            mobileNav.setAttribute('aria-hidden', isExpanded);
        });
        
        // Close menu when clicking a link
        mobileNav.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                hamburger.setAttribute('aria-expanded', 'false');
                mobileNav.setAttribute('aria-hidden', 'true');
            });
        });
        
        // Close menu on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && hamburger.getAttribute('aria-expanded') === 'true') {
                hamburger.setAttribute('aria-expanded', 'false');
                mobileNav.setAttribute('aria-hidden', 'true');
            }
        });
    }

    // ========================================================
    // Form Validation
    // ========================================================
    
    function validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }
    
    function validatePassword(password) {
        // Min 10 chars, at least 1 uppercase, 1 lowercase, 1 number
        return password.length >= 10 &&
               /[A-Z]/.test(password) &&
               /[a-z]/.test(password) &&
               /[0-9]/.test(password);
    }
    
    function initFormValidation() {
        const emailInputs = document.querySelectorAll('input[type="email"]');
        const passwordInputs = document.querySelectorAll('input[type="password"]');
        
        // Email validation (real-time)
        emailInputs.forEach(input => {
            input.addEventListener('blur', () => {
                const isValid = input.value === '' || validateEmail(input.value);
                if (input.value !== '') {
                    input.setAttribute('aria-invalid', !isValid);
                    input.classList.toggle('input-error', !isValid);
                    input.classList.toggle('input-valid', isValid);
                }
            });
            
            input.addEventListener('input', () => {
                if (input.getAttribute('aria-invalid') === 'true') {
                    const isValid = validateEmail(input.value);
                    input.setAttribute('aria-invalid', !isValid);
                    input.classList.toggle('input-error', !isValid);
                    input.classList.toggle('input-valid', isValid);
                }
            });
        });
        
        // Password validation (with strength meter)
        passwordInputs.forEach(input => {
            const strengthContainer = input.parentElement.querySelector('.password-strength');
            if (strengthContainer) {
                input.addEventListener('input', () => {
                    updatePasswordStrength(input.value, strengthContainer);
                });
                
                // Initialize on load if password field has a value
                if (input.value) {
                    updatePasswordStrength(input.value, strengthContainer);
                }
            }
        });
    }
    
    function updatePasswordStrength(password, container) {
        const progress = container.querySelector('progress');
        const hint = container.querySelector('small');
        
        let strength = 0;
        let feedback = 'Very weak password';
        
        // Length check
        if (password.length >= 8) strength += 20;
        if (password.length >= 12) strength += 20;
        
        // Uppercase check
        if (/[A-Z]/.test(password)) strength += 20;
        
        // Lowercase check
        if (/[a-z]/.test(password)) strength += 20;
        
        // Number check
        if (/[0-9]/.test(password)) strength += 20;
        
        // Special characters check
        if (/[!@#$%^&*]/.test(password)) strength += 10;
        
        // Update progress bar
        if (progress) {
            progress.value = Math.min(strength, 100);
        }
        
        // Update feedback text
        if (hint) {
            if (strength < 40) {
                feedback = 'Weak password - Add uppercase, numbers, and more length';
                container.className = 'password-strength weak';
            } else if (strength < 70) {
                feedback = 'Fair password - Could use special characters or more length';
                container.className = 'password-strength fair';
            } else if (strength < 100) {
                feedback = 'Good password - Consider adding special characters';
                container.className = 'password-strength good';
            } else {
                feedback = 'Strong password ✓ Ready to use';
                container.className = 'password-strength good';
            }
            hint.textContent = feedback;
        }
    }

    // ========================================================
    // Dropzone Drag & Drop
    // ========================================================
    
    function initDropzone() {
        const dropzones = document.querySelectorAll('.dropzone');
        
        dropzones.forEach(zone => {
            const input = zone.querySelector('input[type="file"]');
            if (!input) return;
            
            // Prevent default drag behaviors
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                zone.addEventListener(eventName, preventDefaults, false);
                document.body.addEventListener(eventName, preventDefaults, false);
            });
            
            // Highlight drop zone when item is dragged over it
            ['dragenter', 'dragover'].forEach(eventName => {
                zone.addEventListener(eventName, () => zone.classList.add('drag-over'), false);
            });
            
            ['dragleave', 'drop'].forEach(eventName => {
                zone.addEventListener(eventName, () => zone.classList.remove('drag-over'), false);
            });
            
            // Handle dropped files
            zone.addEventListener('drop', (e) => {
                const dt = e.dataTransfer;
                const files = dt.files;
                input.files = files;
                
                // Trigger change event so form can react
                input.dispatchEvent(new Event('change', { bubbles: true }));
            }, false);
        });
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
    }

    // ========================================================
    // Form Submit Validation
    // ========================================================
    
    function initFormSubmit() {
        const forms = document.querySelectorAll('form');
        
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                const requiredInputs = form.querySelectorAll('[required]');
                let hasErrors = false;
                
                requiredInputs.forEach(input => {
                    if (!input.value.trim()) {
                        input.setAttribute('aria-invalid', 'true');
                        input.classList.add('input-error');
                        hasErrors = true;
                    }
                });
                
                // Check email fields
                const emailInputs = form.querySelectorAll('input[type="email"]');
                emailInputs.forEach(input => {
                    if (input.value && !validateEmail(input.value)) {
                        input.setAttribute('aria-invalid', 'true');
                        input.classList.add('input-error');
                        hasErrors = true;
                    }
                });
                
                // Check password confirmation if present
                const passwordInput = form.querySelector('input[name="password"]');
                const confirmInput = form.querySelector('input[name="confirm_password"], input[name="confirm-password"]');
                if (passwordInput && confirmInput && passwordInput.value !== confirmInput.value) {
                    confirmInput.setAttribute('aria-invalid', 'true');
                    confirmInput.classList.add('input-error');
                    hasErrors = true;
                    
                    // Show error message
                    const errorMsg = document.createElement('div');
                    errorMsg.className = 'alert alert-error';
                    errorMsg.setAttribute('role', 'alert');
                    errorMsg.textContent = 'Passwords do not match.';
                    form.insertBefore(errorMsg, form.firstChild);
                    
                    // Remove after 5 seconds
                    setTimeout(() => errorMsg.remove(), 5000);
                }
                
                if (hasErrors) {
                    e.preventDefault();
                    
                    // Focus first error field
                    const firstError = form.querySelector('[aria-invalid="true"]');
                    if (firstError) firstError.focus();
                }
            });
        });
    }

    // ========================================================
    // Table Sorting (Basic)
    // ========================================================
    
    function initTableSorting() {
        const tables = document.querySelectorAll('table');
        
        tables.forEach(table => {
            const headers = table.querySelectorAll('th.table-sortable');
            
            headers.forEach((header, index) => {
                header.addEventListener('click', () => {
                    const sortOrder = header.getAttribute('aria-sort');
                    const newOrder = sortOrder === 'ascending' ? 'descending' : 'ascending';
                    
                    // Reset other headers
                    headers.forEach(h => h.setAttribute('aria-sort', 'none'));
                    
                    // Set this header's order
                    header.setAttribute('aria-sort', newOrder);
                    
                    // In a real app, this would sort the table rows
                    // For now, it just updates the visual indicator
                });
            });
        });
    }

    // ========================================================
    // Dark Mode Toggle (Phase 4)
    // ========================================================
    
    function initDarkModeToggle() {
        const themeToggle = document.getElementById('theme-toggle');
        if (!themeToggle) return;
        
        const html = document.documentElement;
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        // Set initial theme based on localStorage or system preference
        const storedTheme = localStorage.getItem('theme');
        const currentTheme = storedTheme || (prefersDark ? 'dark' : 'light');
        
        // Update button icon to show opposite theme
        const updateIcon = (theme) => {
            themeToggle.textContent = theme === 'dark' ? '☀️' : '🌙';
        };
        
        // Apply stored theme on page load
        if (currentTheme === 'dark') {
            html.setAttribute('data-theme', 'dark');
            updateIcon('dark');
        }
        
        // Toggle theme on button click
        themeToggle.addEventListener('click', () => {
            const isDark = html.getAttribute('data-theme') === 'dark';
            const newTheme = isDark ? 'light' : 'dark';
            
            html.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateIcon(newTheme);
        });
        
        // Listen to system preference changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (!localStorage.getItem('theme')) {
                const newTheme = e.matches ? 'dark' : 'light';
                html.setAttribute('data-theme', newTheme);
                updateIcon(newTheme);
            }
        });
    }

    // ========================================================
    // Initialize on DOM Ready
    // ========================================================
    
    function init() {
        // Only initialize if DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
            return;
        }
        
        initHamburgerMenu();
        initFormValidation();
        initFormSubmit();
        initDropzone();
        initTableSorting();
        initDarkModeToggle();  // Phase 4
    }
    
    // Start initialization
    init();
})();
