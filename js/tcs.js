/**
 * Tirumala Consultancy Services (TCS) - Core Interaction Script
 * Standalone, lightweight, zero-dependency client logic.
 */
function initTCS() {
    // 0. Ensure all logos navigate to home page on click
    document.querySelectorAll('img[src*="logo"], img[alt*="logo" i]').forEach(img => {
        const link = img.closest('a');
        if (link) {
            link.href = './index.html';
        } else {
            img.style.cursor = 'pointer';
            img.addEventListener('click', () => {
                window.location.href = './index.html';
            });
        }
    });

    // 1. Navbar Mega Menu Hover & Interaction Logic (Rock-solid intent & diagonal protection)
    const navGroups = document.querySelectorAll('nav .group');
    const closeTimers = new Map();

    function openNavGroup(group) {
        // Clear any pending close timer for this group
        if (closeTimers.has(group)) {
            clearTimeout(closeTimers.get(group));
            closeTimers.delete(group);
        }

        // Close all other open groups immediately to prevent collision
        navGroups.forEach(other => {
            if (other !== group) {
                if (closeTimers.has(other)) {
                    clearTimeout(closeTimers.get(other));
                    closeTimers.delete(other);
                }
                other.classList.remove('is-open');
                const otherBoxes = other.querySelectorAll('.group-hover\\:block');
                const otherLink = other.querySelector('a');
                otherBoxes.forEach(b => {
                    b.style.display = '';
                    b.style.visibility = '';
                    b.style.opacity = '';
                    b.style.pointerEvents = '';
                });
                if (otherLink) otherLink.setAttribute('aria-expanded', 'false');
            }
        });

        // Open this group
        group.classList.add('is-open');
        const dropdownBoxes = group.querySelectorAll('.group-hover\\:block');
        const topLink = group.querySelector('a');
        dropdownBoxes.forEach(box => {
            box.style.display = 'block';
            box.style.visibility = 'visible';
            box.style.opacity = '1';
            box.style.pointerEvents = 'auto';
        });
        if (topLink) topLink.setAttribute('aria-expanded', 'true');
    }

    function closeNavGroup(group, delay = 200) {
        if (closeTimers.has(group)) {
            clearTimeout(closeTimers.get(group));
        }
        const timer = setTimeout(() => {
            group.classList.remove('is-open');
            const dropdownBoxes = group.querySelectorAll('.group-hover\\:block');
            const topLink = group.querySelector('a');
            dropdownBoxes.forEach(box => {
                box.style.display = '';
                box.style.visibility = '';
                box.style.opacity = '';
                box.style.pointerEvents = '';
            });
            if (topLink) topLink.setAttribute('aria-expanded', 'false');
            closeTimers.delete(group);
        }, delay);
        closeTimers.set(group, timer);
    }

    navGroups.forEach(group => {
        const topLink = group.querySelector('a');
        const dropdownBoxes = group.querySelectorAll('.group-hover\\:block');

        if (topLink) {
            topLink.setAttribute('role', 'button');
            topLink.setAttribute('aria-haspopup', 'true');
            topLink.setAttribute('aria-expanded', 'false');
            topLink.style.cursor = 'pointer';

            // Top-level item click toggles menu smoothly
            topLink.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                if (group.classList.contains('is-open')) {
                    closeNavGroup(group, 0);
                } else {
                    openNavGroup(group);
                }
            });
        }

        // Enter: immediately open and cancel any pending close
        group.addEventListener('mouseenter', function() {
            openNavGroup(group);
        });

        // Leave: grace period allows diagonal transit without flickering or premature closing
        group.addEventListener('mouseleave', function() {
            closeNavGroup(group, 220);
        });

        // Touch support
        group.addEventListener('touchstart', function(e) {
            const isCurrentlyOpen = group.classList.contains('is-open');
            if (!isCurrentlyOpen) {
                openNavGroup(group);
            }
        }, { passive: true });
    });

    // Close any open dropdown when clicking outside navbar
    document.addEventListener('click', function(e) {
        if (!e.target.closest('nav .group')) {
            navGroups.forEach(group => closeNavGroup(group, 0));
        }
    });

    // 2. Intersection Observer for Scroll Animations
    if ('IntersectionObserver' in window) {
        const cardObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('opacity-100', 'translate-y-0');
                    entry.target.classList.remove('opacity-0', 'translate-y-8');
                    cardObserver.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });

        document.querySelectorAll('.ifcFeatureCard, .ifcProcessCard').forEach(el => {
            el.classList.add('opacity-0', 'translate-y-8', 'transition-all', 'duration-700', 'ease-out');
            cardObserver.observe(el);
        });

        const revealObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    Array.from(entry.target.classList).forEach(cls => {
                        if (cls.includes('reveal') && !cls.includes('Visible')) {
                            entry.target.classList.add(cls + 'Visible');
                        }
                    });
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: "0px 0px -50px 0px"
        });

        document.querySelectorAll('[class*="reveal"]').forEach(el => revealObserver.observe(el));
    }

    // 3. FAQ Accordion & Load More (Service Pages & Generic)
    const faqCards = document.querySelectorAll('.ifcFaqCard');
    const loadMoreBtn = document.querySelector('.ifcFaqBtnPrimary, [class*="ifcFaqBtn"]');
    let visibleCount = 6;

    if (faqCards.length > 0) {
        faqCards.forEach((card, index) => {
            if (card.tagName === 'SECTION' || card.id === 'faq-section' || card.id === 'faq-heading') return;
            if (index >= visibleCount && card.classList.contains('ifcFaqCard')) {
                card.style.display = 'none';
            }
            
            const btn = card.querySelector('button[aria-controls], .ifcFaqCardBtn, button');
            const answer = card.querySelector('[role="region"], div[id^="faq-answer-"], div.overflow-hidden');
            const chevron = card.querySelector('.ifcFaqCardChevron, svg');
            
            if (btn && answer) {
                btn.addEventListener('click', () => {
                    const isExpanded = btn.getAttribute('aria-expanded') === 'true';
                    
                    // Close other FAQ items
                    faqCards.forEach(otherCard => {
                        if (otherCard !== card) {
                            const otherBtn = otherCard.querySelector('button[aria-controls], .ifcFaqCardBtn, button');
                            const otherAns = otherCard.querySelector('[role="region"], div[id^="faq-answer-"], div.overflow-hidden');
                            const otherChev = otherCard.querySelector('.ifcFaqCardChevron, svg');
                            if (otherBtn) otherBtn.setAttribute('aria-expanded', 'false');
                            if (otherAns) otherAns.style.gridTemplateRows = '0fr';
                            if (otherChev) otherChev.classList.remove('ifcFaqCardChevronOpen');
                            otherCard.classList.remove('ifcFaqCardOpen');
                        }
                    });

                    // Toggle current item
                    btn.setAttribute('aria-expanded', !isExpanded);
                    answer.style.gridTemplateRows = isExpanded ? '0fr' : '1fr';
                    if (isExpanded) {
                        if (chevron) chevron.classList.remove('ifcFaqCardChevronOpen');
                        card.classList.remove('ifcFaqCardOpen');
                    } else {
                        if (chevron) chevron.classList.add('ifcFaqCardChevronOpen');
                        card.classList.add('ifcFaqCardOpen');
                    }
                });
            }
        });

        if (loadMoreBtn) {
            loadMoreBtn.addEventListener('click', () => {
                const isExpanded = visibleCount > 6;
                if (isExpanded) {
                    visibleCount = 6;
                    loadMoreBtn.innerText = 'Load more questions';
                } else {
                    visibleCount = faqCards.length;
                    loadMoreBtn.innerText = 'Show less';
                }
                
                faqCards.forEach((card, index) => {
                    if (index < visibleCount) {
                        card.style.display = 'block';
                    } else {
                        card.style.display = 'none';
                        const btn = card.querySelector('button');
                        const answer = card.querySelector('[role="region"], div.overflow-hidden');
                        const chevron = card.querySelector('.ifcFaqCardChevron, svg');
                        if (btn) btn.setAttribute('aria-expanded', 'false');
                        if (answer) answer.style.gridTemplateRows = '0fr';
                        if (chevron) chevron.classList.remove('ifcFaqCardChevronOpen');
                        card.classList.remove('ifcFaqCardOpen');
                    }
                });
            });
        }
    }

    // 4. Homepage FAQ Accordion
    const homeFaqBtns = document.querySelectorAll('.index-module__vbPTMW__faqButton');
    homeFaqBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const isExpanded = btn.getAttribute('aria-expanded') === 'true';
            const answer = btn.nextElementSibling;
            const chevron = btn.querySelector('.index-module__vbPTMW__faqChevron');

            homeFaqBtns.forEach(otherBtn => {
                if (otherBtn !== btn) {
                    otherBtn.setAttribute('aria-expanded', 'false');
                    const otherAns = otherBtn.nextElementSibling;
                    const otherChev = otherBtn.querySelector('.index-module__vbPTMW__faqChevron');
                    if (otherAns) {
                        otherAns.style.maxHeight = '0';
                        otherAns.style.opacity = '0';
                    }
                    if (otherChev) otherChev.classList.remove('index-module__vbPTMW__faqChevronOpen');
                }
            });

            btn.setAttribute('aria-expanded', !isExpanded);
            if (answer) {
                if (isExpanded) {
                    answer.style.maxHeight = '0';
                    answer.style.opacity = '0';
                } else {
                    answer.style.maxHeight = answer.scrollHeight + 'px';
                    answer.style.opacity = '1';
                }
            }
            if (chevron) {
                chevron.classList.toggle('index-module__vbPTMW__faqChevronOpen', !isExpanded);
            }
        });
    });

    // 5. Complete Accessible Mobile Navigation System
    function initMobileNavigation() {
        const openBtn = document.querySelector('button[aria-label="Open menu"]');
        if (!openBtn) return;

        let mobileMenu = document.getElementById('tcs-mobile-menu');

        // Dynamically construct mobile menu drawer from desktop nav if not already in DOM
        if (!mobileMenu) {
            mobileMenu = document.createElement('div');
            mobileMenu.id = 'tcs-mobile-menu';
            mobileMenu.setAttribute('role', 'dialog');
            mobileMenu.setAttribute('aria-modal', 'true');
            mobileMenu.setAttribute('aria-label', 'Mobile Navigation');

            // Backdrop
            const backdrop = document.createElement('div');
            backdrop.className = 'tcs-mobile-backdrop';
            backdrop.setAttribute('aria-hidden', 'true');
            mobileMenu.appendChild(backdrop);

            // Drawer
            const drawer = document.createElement('div');
            drawer.className = 'tcs-mobile-drawer';

            // Header
            const header = document.createElement('div');
            header.className = 'tcs-mobile-drawer-header';
            header.innerHTML = `
                <a href="./index.html" class="flex items-center gap-2" aria-label="Tirumala Consultancy Services">
                    <img src="./images/tcs_logo.png" alt="TCS Logo" style="height:34px;width:auto;object-fit:contain" />
                </a>
                <button type="button" class="tcs-mobile-close-btn" aria-label="Close menu">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </button>
            `;
            drawer.appendChild(header);

            // Body
            const body = document.createElement('div');
            body.className = 'tcs-mobile-drawer-body';

            // Extract categories and links from desktop nav
            const desktopNavGroups = document.querySelectorAll('header nav .group, nav .group');
            if (desktopNavGroups.length > 0) {
                desktopNavGroups.forEach((group, idx) => {
                    const topLink = group.querySelector('a');
                    const categoryName = topLink ? topLink.textContent.trim() : `Category ${idx + 1}`;
                    const sublinks = group.querySelectorAll('.group-hover\\:block a, div.absolute a');

                    const item = document.createElement('div');
                    item.className = 'tcs-mobile-accordion-item';

                    const itemBtn = document.createElement('button');
                    itemBtn.type = 'button';
                    itemBtn.className = 'tcs-mobile-accordion-btn';
                    itemBtn.setAttribute('aria-expanded', 'false');
                    itemBtn.innerHTML = `
                        <span>${categoryName}</span>
                        <svg class="tcs-mobile-accordion-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <polyline points="6 9 12 15 18 9"></polyline>
                        </svg>
                    `;

                    const panel = document.createElement('div');
                    panel.className = 'tcs-mobile-accordion-panel';

                    const linksContainer = document.createElement('div');
                    linksContainer.className = 'flex flex-col gap-0.5';

                    sublinks.forEach(sub => {
                        const href = sub.getAttribute('href');
                        const text = sub.textContent.trim();
                        if (href && text && !href.startsWith('javascript:')) {
                            const a = document.createElement('a');
                            a.href = href;
                            a.className = 'tcs-mobile-sublink';
                            a.textContent = text;
                            a.addEventListener('click', closeMenu);
                            linksContainer.appendChild(a);
                        }
                    });

                    panel.appendChild(linksContainer);

                    // Accordion toggle
                    itemBtn.addEventListener('click', (e) => {
                        e.preventDefault();
                        const isExpanded = item.classList.contains('is-expanded');
                        
                        // Close other categories for clean single accordion
                        drawer.querySelectorAll('.tcs-mobile-accordion-item').forEach(other => {
                            if (other !== item) {
                                other.classList.remove('is-expanded');
                                const otherBtn = other.querySelector('.tcs-mobile-accordion-btn');
                                if (otherBtn) otherBtn.setAttribute('aria-expanded', 'false');
                            }
                        });

                        item.classList.toggle('is-expanded', !isExpanded);
                        itemBtn.setAttribute('aria-expanded', !isExpanded ? 'true' : 'false');
                    });

                    item.appendChild(itemBtn);
                    item.appendChild(panel);
                    body.appendChild(item);
                });
            }

            drawer.appendChild(body);

            // Footer with approved CTA Gradient
            const footer = document.createElement('div');
            footer.className = 'tcs-mobile-drawer-footer';
            footer.innerHTML = `
                <a href="./contact.html#talk-to-experts" class="tcs-mobile-cta-btn" onclick="closeMenu()">
                    <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/></svg>
                    <span>Talk to an Expert</span>
                </a>
            `;
            drawer.appendChild(footer);

            mobileMenu.appendChild(drawer);
            document.body.appendChild(mobileMenu);

            backdrop.addEventListener('click', closeMenu);
            const closeBtn = drawer.querySelector('.tcs-mobile-close-btn');
            if (closeBtn) closeBtn.addEventListener('click', closeMenu);
        }

        function openMenu() {
            mobileMenu.classList.add('is-open');
            openBtn.setAttribute('aria-expanded', 'true');
            document.body.style.overflow = 'hidden';
            document.documentElement.style.overflow = 'hidden';
        }

        function closeMenu() {
            mobileMenu.classList.remove('is-open');
            openBtn.setAttribute('aria-expanded', 'false');
            document.body.style.overflow = '';
            document.documentElement.style.overflow = '';
        }

        openBtn.addEventListener('click', (e) => {
            e.preventDefault();
            if (mobileMenu.classList.contains('is-open')) {
                closeMenu();
            } else {
                openMenu();
            }
        });

        // Close on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && mobileMenu.classList.contains('is-open')) {
                closeMenu();
            }
        });

        // Auto-close on viewport resize to desktop (>= 1024px)
        window.addEventListener('resize', () => {
            if (window.innerWidth >= 1024 && mobileMenu.classList.contains('is-open')) {
                closeMenu();
            }
        });
    }

    initMobileNavigation();

    // 6. Clean Form Handling
    document.querySelectorAll('form').forEach(form => {
        if (form.id === 'tcs-enquiry-form') return; // Handled with dedicated validation in initContactPageLogic
        form.addEventListener('submit', function(e) {
            const action = form.getAttribute('action') || '';
            if (!action || action === '#' || !action.startsWith('http')) {
                e.preventDefault();
                const btn = form.querySelector('button[type="submit"]');
                if (btn) {
                    const originalText = btn.innerText;
                    btn.innerText = 'Enquiry Submitted Successfully!';
                    btn.disabled = true;
                    setTimeout(() => {
                        btn.innerText = originalText;
                        btn.disabled = false;
                        form.reset();
                    }, 3500);
                }
            }
        });
    });

    // 7. Contact Page Service Pre-selection & Outcrowd-Style Form Validation
    function initContactPageLogic() {
        const contactForm = document.getElementById('tcs-enquiry-form');
        const serviceSelect = document.getElementById('contact_service');
        const successBox = document.getElementById('tcs-form-success');

        // Form Validation & Submission
        if (contactForm) {
            const nameInput = document.getElementById('contact_name');
            const phoneInput = document.getElementById('contact_phone');
            const emailInput = document.getElementById('contact_email');
            const reqTextarea = document.getElementById('contact_requirement');
            const submitBtn = document.getElementById('submit-enquiry-btn');

            function setError(inputEl, errorId, show) {
                if (!inputEl) return;
                const errEl = document.getElementById(errorId);
                if (show) {
                    inputEl.classList.add('has-error');
                    if (errEl) errEl.style.display = 'block';
                } else {
                    inputEl.classList.remove('has-error');
                    if (errEl) errEl.style.display = 'none';
                }
            }

            // Real-time error clearance on input
            if (nameInput) {
                nameInput.addEventListener('input', () => {
                    if (nameInput.value.trim().length >= 2) setError(nameInput, 'error_contact_name', false);
                });
            }
            if (phoneInput) {
                phoneInput.addEventListener('input', () => {
                    const cleanPhone = phoneInput.value.replace(/[^0-9]/g, '');
                    if (cleanPhone.length >= 7) setError(phoneInput, 'error_contact_phone', false);
                });
            }
            if (emailInput) {
                emailInput.addEventListener('input', () => {
                    const val = emailInput.value.trim();
                    if (!val || (val.includes('@') && val.includes('.'))) setError(emailInput, 'error_contact_email', false);
                });
            }
            if (serviceSelect) {
                serviceSelect.addEventListener('change', () => {
                    if (serviceSelect.value) setError(serviceSelect, 'error_contact_service', false);
                });
            }
            if (reqTextarea) {
                reqTextarea.addEventListener('input', () => {
                    if (reqTextarea.value.trim().length >= 3) setError(reqTextarea, 'error_contact_requirement', false);
                });
            }

            contactForm.addEventListener('submit', function(e) {
                e.preventDefault();
                let hasError = false;

                // Validate Name
                if (!nameInput || nameInput.value.trim().length < 2) {
                    setError(nameInput, 'error_contact_name', true);
                    hasError = true;
                } else {
                    setError(nameInput, 'error_contact_name', false);
                }

                // Validate Phone
                const cleanPhone = phoneInput ? phoneInput.value.replace(/[^0-9]/g, '') : '';
                if (!phoneInput || cleanPhone.length < 7) {
                    setError(phoneInput, 'error_contact_phone', true);
                    hasError = true;
                } else {
                    setError(phoneInput, 'error_contact_phone', false);
                }

                // Validate Email (optional, but must be valid format if provided)
                if (emailInput && emailInput.value.trim() !== '') {
                    const emailVal = emailInput.value.trim();
                    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                    if (!emailRegex.test(emailVal)) {
                        setError(emailInput, 'error_contact_email', true);
                        hasError = true;
                    } else {
                        setError(emailInput, 'error_contact_email', false);
                    }
                } else if (emailInput) {
                    setError(emailInput, 'error_contact_email', false);
                }

                // Validate Service
                if (!serviceSelect || !serviceSelect.value) {
                    setError(serviceSelect, 'error_contact_service', true);
                    hasError = true;
                } else {
                    setError(serviceSelect, 'error_contact_service', false);
                }

                // Validate Requirement
                if (!reqTextarea || reqTextarea.value.trim().length < 3) {
                    setError(reqTextarea, 'error_contact_requirement', true);
                    hasError = true;
                } else {
                    setError(reqTextarea, 'error_contact_requirement', false);
                }

                if (hasError) return;

                // Submit state
                if (submitBtn) {
                    const originalHtml = submitBtn.innerHTML;
                    submitBtn.innerHTML = `
                        <span>Submitting enquiry...</span>
                        <svg class="animate-spin" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10" stroke-opacity="0.25"></circle><path d="M12 2a10 10 0 0 1 10 10" stroke-linecap="round"></path></svg>
                    `;
                    submitBtn.disabled = true;

                    setTimeout(() => {
                        submitBtn.innerHTML = `
                            <span>Enquiry Submitted ✓</span>
                        `;
                        submitBtn.style.background = '#16A34A';
                        if (successBox) {
                            successBox.style.display = 'flex';
                            successBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                        }
                        contactForm.reset();

                        setTimeout(() => {
                            submitBtn.innerHTML = originalHtml;
                            submitBtn.style.background = '';
                            submitBtn.disabled = false;
                        }, 5000);
                    }, 800);
                }
            });
        }

        // Service Pre-selection via URL Parameter
        if (serviceSelect) {
            const urlParams = new URLSearchParams(window.location.search);
            const serviceParam = urlParams.get('service');
            if (serviceParam && serviceParam.trim() !== '') {
                const cleanParam = serviceParam.trim().toLowerCase();
                const normalizedParam = cleanParam.replace(/[-_]/g, '');
                let matchedIndex = -1;

                // 1. Exact match on value
                for (let i = 1; i < serviceSelect.options.length; i++) {
                    const opt = serviceSelect.options[i];
                    if (opt.value && opt.value.toLowerCase() === cleanParam) {
                        matchedIndex = i;
                        break;
                    }
                }

                // 2. Normalized match (ignoring dashes/underscores)
                if (matchedIndex === -1) {
                    for (let i = 1; i < serviceSelect.options.length; i++) {
                        const opt = serviceSelect.options[i];
                        const optVal = opt.value ? opt.value.toLowerCase().replace(/[-_]/g, '') : '';
                        if (optVal && optVal === normalizedParam) {
                            matchedIndex = i;
                            break;
                        }
                    }
                }

                // 3. Substring match on option text or value
                if (matchedIndex === -1) {
                    for (let i = 1; i < serviceSelect.options.length; i++) {
                        const opt = serviceSelect.options[i];
                        const optVal = opt.value ? opt.value.toLowerCase().replace(/[-_]/g, '') : '';
                        const optText = opt.text.toLowerCase().replace(/[^a-z0-9]/g, '');
                        if (optText.includes(normalizedParam) || (optVal && (normalizedParam.includes(optVal) || optVal.includes(normalizedParam)))) {
                            matchedIndex = i;
                            break;
                        }
                    }
                }

                if (matchedIndex > 0) {
                    serviceSelect.selectedIndex = matchedIndex;
                    serviceSelect.options[matchedIndex].selected = true;
                }
            }
        }

        // Outcrowd-inspired Explode / Cursor-following Ripple Effect
        document.querySelectorAll('.tcs-has-explode').forEach(button => {
            const explode = button.querySelector('.tcs-explode');
            if (!explode) return;

            button.addEventListener('mousemove', (e) => {
                const rect = button.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;

                explode.style.left = `${x}px`;
                explode.style.top = `${y}px`;
                button.classList.add('is-exploding');
            });

            button.addEventListener('mouseleave', () => {
                button.classList.remove('is-exploding');
            });
        });

        // Outcrowd-inspired Magnetic Hover Effect
        const magneticElements = document.querySelectorAll('.tcs-magnetic');
        const magnetStrength = 8;

        magneticElements.forEach(el => {
            el.addEventListener('mousemove', (e) => {
                const rect = el.getBoundingClientRect();
                const centerX = rect.left + rect.width / 2;
                const centerY = rect.top + rect.height / 2;

                const distX = ((e.clientX - centerX) / rect.width) * magnetStrength;
                const distY = ((e.clientY - centerY) / rect.height) * magnetStrength;

                el.style.transform = `translate(${distX}px, ${distY}px)`;
            });

            el.addEventListener('mouseleave', () => {
                el.style.transform = 'translate(0, 0)';
            });
        });

        // Outcrowd-inspired Scroll-based Header Transformation
        const headerEl = document.querySelector('.ifLayoutHeader');
        if (headerEl) {
            function updateHeaderOnScroll() {
                const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                if (scrollTop > 20) {
                    headerEl.classList.add('is-scrolled');
                } else {
                    headerEl.classList.remove('is-scrolled');
                }
            }
            window.addEventListener('scroll', updateHeaderOnScroll, { passive: true });
            updateHeaderOnScroll();
        }

        // Handle #talk-to-experts smooth scrolling
        function scrollToExperts() {
            const target = document.getElementById('talk-to-experts');
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }

        if (window.location.hash === '#talk-to-experts') {
            setTimeout(scrollToExperts, 150);
        }

        document.querySelectorAll('a[href="#talk-to-experts"], a[href="./contact.html#talk-to-experts"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                const isCurrentPage = window.location.pathname.endsWith('contact.html') || window.location.pathname.endsWith('/contact');
                if (isCurrentPage) {
                    e.preventDefault();
                    scrollToExperts();
                    history.pushState(null, '', '#talk-to-experts');
                }
            });
        });
    }

    initContactPageLogic();
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTCS);
} else {
    initTCS();
}
