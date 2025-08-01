// Quick Help Functions
function showQuickHelpContent(type) {
    let modalId = '';
    switch(type) {
        case 'getting-started':
            modalId = 'gettingStartedModal';
            break;
        case 'video-tutorials':
            modalId = 'videoTutorialsModal';
            break;
        case 'documentation':
            modalId = 'documentationModal';
            break;
        case 'faqs':
            modalId = 'faqsModal';
            break;
    }
    
    if (modalId) {
        const modal = new bootstrap.Modal(document.getElementById(modalId));
        modal.show();
    }
}

function showQuickHelpEditor() {
    const modal = new bootstrap.Modal(document.getElementById('quickHelpEditorModal'));
    modal.show();
}

function playVideo(videoId, title, description) {
    document.getElementById('videoTitle').textContent = title;
    document.getElementById('videoDescription').textContent = description;
    
    // Update video player area
    const videoContainer = document.querySelector('.video-container');
    videoContainer.innerHTML = `
        <div class="text-center text-white">
            <i class="fas fa-play-circle fa-3x mb-3"></i>
            <p>Playing: ${title}</p>
            <small>Video ID: ${videoId}</small>
        </div>
    `;
}

function downloadVideo() {
    alert('Video download feature will be implemented soon.');
}

function showDocSection(section) {
    // Update active nav item
    document.querySelectorAll('.doc-sidebar .list-group-item').forEach(item => {
        item.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Show content for selected section
    alert(`Showing ${section} documentation section.`);
}

function exportDocumentation() {
    alert('Documentation export feature will be implemented soon.');
}

function submitFAQ() {
    alert('FAQ submission feature will be implemented soon.');
}

function startTutorial() {
    alert('Interactive tutorial will be implemented soon.');
}

function saveQuickHelpContent() {
    alert('Content saved successfully!');
    const modal = bootstrap.Modal.getInstance(document.getElementById('quickHelpEditorModal'));
    modal.hide();
}

// Add click handlers to Quick Help items
document.addEventListener('DOMContentLoaded', function() {
    // Make Quick Help items clickable
    const quickHelpItems = document.querySelectorAll('.quick-help .list-group-item');
    quickHelpItems.forEach((item, index) => {
        item.style.cursor = 'pointer';
        item.addEventListener('click', function() {
            const types = ['getting-started', 'video-tutorials', 'documentation', 'faqs'];
            if (types[index]) {
                showQuickHelpContent(types[index]);
            }
        });
    });
    
    // Add edit button for admins
    const quickHelpSection = document.querySelector('.quick-help');
    if (quickHelpSection && document.body.classList.contains('admin-user')) {
        const editButton = document.createElement('button');
        editButton.className = 'btn btn-sm btn-outline-primary float-end';
        editButton.innerHTML = '<i class="fas fa-edit me-1"></i>Edit Content';
        editButton.onclick = showQuickHelpEditor;
        
        const header = quickHelpSection.querySelector('h6');
        if (header) {
            header.appendChild(editButton);
        }
    }
}); 