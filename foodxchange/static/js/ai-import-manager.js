/**
 * AI-Powered Import Manager
 * Handles intelligent field mapping and import workflow
 */

class AIImportManager {
    constructor() {
        this.currentStep = 'upload';
        this.analysisData = null;
        this.mappingConfirmations = {};
        this.fileInfo = null;
        this.importType = 'suppliers'; // Default
    }

    // Initialize the import process
    init(importType) {
        this.importType = importType;
        this.currentStep = 'upload';
        this.setupEventListeners();
        this.renderCurrentStep();
    }

    // Setup event listeners
    setupEventListeners() {
        // File upload
        document.addEventListener('change', (e) => {
            if (e.target.id === 'importFile') {
                this.handleFileUpload(e.target.files[0]);
            }
        });

        // Step navigation
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('step-nav-btn')) {
                const step = e.target.dataset.step;
                if (step) this.navigateToStep(step);
            }
        });
    }

    // Handle file upload
    async handleFileUpload(file) {
        if (!file) return;

        this.fileInfo = {
            name: file.name,
            size: file.size,
            type: file.type
        };

        // Show upload progress
        this.showProgress('Uploading file...');

        const formData = new FormData();
        formData.append('file', file);
        formData.append('data_type', this.importType);

        try {
            // Upload and analyze with AI
            const response = await fetch('/api/import/analyze-ai', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                this.analysisData = result.data;
                this.navigateToStep('analysis');
            } else {
                this.showError(result.error || 'Failed to analyze file');
            }
        } catch (error) {
            this.showError('Upload failed: ' + error.message);
        }
    }

    // Navigate to a specific step
    navigateToStep(step) {
        this.currentStep = step;
        this.renderCurrentStep();
    }

    // Render the current step
    renderCurrentStep() {
        const container = document.getElementById('importContainer');
        if (!container) return;

        let content = '';

        switch (this.currentStep) {
            case 'upload':
                content = this.renderUploadStep();
                break;
            case 'analysis':
                content = this.renderAnalysisStep();
                break;
            case 'mapping':
                content = this.renderMappingStep();
                break;
            case 'preview':
                content = this.renderPreviewStep();
                break;
            case 'validation':
                content = this.renderValidationStep();
                break;
            case 'complete':
                content = this.renderCompleteStep();
                break;
        }

        container.innerHTML = content;
        this.attachStepHandlers();
    }

    // Render upload step
    renderUploadStep() {
        return `
            <div class="import-step upload-step">
                <div class="step-header">
                    <h3>Upload ${this.importType} Data</h3>
                    <p>Select a CSV or Excel file to import</p>
                </div>
                
                <div class="upload-area">
                    <div class="upload-dropzone" id="dropZone">
                        <i class="fas fa-cloud-upload-alt fa-3x mb-3"></i>
                        <h4>Drop your file here or click to browse</h4>
                        <p class="text-muted">Supports CSV, XLS, and XLSX files</p>
                        <input type="file" id="importFile" accept=".csv,.xls,.xlsx" class="d-none">
                        <button class="btn btn-primary mt-3" onclick="document.getElementById('importFile').click()">
                            Choose File
                        </button>
                    </div>
                </div>
                
                <div class="ai-features mt-4">
                    <h5>AI-Powered Features:</h5>
                    <ul class="feature-list">
                        <li><i class="fas fa-check-circle text-success"></i> Automatic field mapping</li>
                        <li><i class="fas fa-check-circle text-success"></i> Data cleaning & standardization</li>
                        <li><i class="fas fa-check-circle text-success"></i> Duplicate detection</li>
                        <li><i class="fas fa-check-circle text-success"></i> Smart validation</li>
                    </ul>
                </div>
            </div>
        `;
    }

    // Render analysis step
    renderAnalysisStep() {
        if (!this.analysisData) return '<div>No analysis data</div>';

        const stats = this.analysisData.sample_data?.stats || {};
        
        return `
            <div class="import-step analysis-step">
                <div class="step-header">
                    <h3>AI Analysis Complete</h3>
                    <p>File analyzed: ${this.fileInfo.name}</p>
                </div>
                
                <div class="analysis-summary">
                    <div class="row">
                        <div class="col-md-4">
                            <div class="stat-card">
                                <h5>${stats.total_rows || 0}</h5>
                                <p>Total Rows</p>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="stat-card">
                                <h5>${stats.total_columns || 0}</h5>
                                <p>Total Columns</p>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="stat-card">
                                <h5>${this.analysisData.mapping_coverage || 0}%</h5>
                                <p>Field Coverage</p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="action-buttons mt-4">
                    <button class="btn btn-secondary" onclick="aiImportManager.navigateToStep('upload')">
                        <i class="fas fa-arrow-left"></i> Back
                    </button>
                    <button class="btn btn-primary" onclick="aiImportManager.navigateToStep('mapping')">
                        Review Mappings <i class="fas fa-arrow-right"></i>
                    </button>
                </div>
            </div>
        `;
    }

    // Render mapping step
    renderMappingStep() {
        if (!this.analysisData) return '<div>No mapping data</div>';

        const confirmed = this.analysisData.confirmed_mappings || [];
        const uncertain = this.analysisData.uncertain_mappings || [];
        const unmapped = this.analysisData.unmapped_fields || [];

        return `
            <div class="import-step mapping-step">
                <div class="step-header">
                    <h3>Field Mapping Review</h3>
                    <p>AI has analyzed your file and suggested the following mappings</p>
                </div>
                
                ${confirmed.length > 0 ? `
                    <div class="mapping-section confirmed-mappings">
                        <h4><i class="fas fa-check-circle text-success"></i> Confirmed Mappings</h4>
                        <div class="mapping-list">
                            ${confirmed.map(mapping => `
                                <div class="mapping-row confirmed">
                                    <div class="source-field">
                                        <span class="field-name">${mapping.source_field}</span>
                                        <small class="sample-values">${this.formatSampleValues(mapping.sample_values)}</small>
                                    </div>
                                    <div class="mapping-arrow">
                                        <i class="fas fa-arrow-right"></i>
                                    </div>
                                    <div class="target-field">
                                        <span class="field-name">${mapping.target_field}</span>
                                        <span class="confidence-badge high">${mapping.confidence}%</span>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
                
                ${uncertain.length > 0 ? `
                    <div class="mapping-section uncertain-mappings mt-4">
                        <h4><i class="fas fa-question-circle text-warning"></i> Please Confirm These Mappings</h4>
                        <div class="mapping-list">
                            ${uncertain.map((mapping, idx) => `
                                <div class="mapping-row uncertain">
                                    <div class="source-field">
                                        <span class="field-name">${mapping.source_field}</span>
                                    </div>
                                    <div class="mapping-arrow">
                                        <i class="fas fa-arrow-right"></i>
                                    </div>
                                    <div class="target-field">
                                        <select class="form-select mapping-select" data-source="${mapping.source_field}">
                                            <option value="">-- Select target field --</option>
                                            ${mapping.suggested_targets.map(target => `
                                                <option value="${target}">${target}</option>
                                            `).join('')}
                                            <option value="_ignore">Ignore this field</option>
                                        </select>
                                        <span class="confidence-badge medium">${mapping.confidence}%</span>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
                
                ${unmapped.length > 0 ? `
                    <div class="mapping-section unmapped-fields mt-4">
                        <h4><i class="fas fa-info-circle text-info"></i> Unmapped Fields</h4>
                        <p class="text-muted">These fields were found but don't match our schema. You can ignore them or create custom fields.</p>
                        <div class="unmapped-list">
                            ${unmapped.map(field => `
                                <div class="unmapped-field">
                                    <span class="field-name">${field.field}</span>
                                    <small class="suggestion">${field.suggestion || ''}</small>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
                
                <div class="action-buttons mt-4">
                    <button class="btn btn-secondary" onclick="aiImportManager.navigateToStep('analysis')">
                        <i class="fas fa-arrow-left"></i> Back
                    </button>
                    <button class="btn btn-primary" onclick="aiImportManager.confirmMappings()">
                        Confirm Mappings <i class="fas fa-arrow-right"></i>
                    </button>
                </div>
            </div>
        `;
    }

    // Render preview step
    renderPreviewStep() {
        return `
            <div class="import-step preview-step">
                <div class="step-header">
                    <h3>Data Preview</h3>
                    <p>Review how your data will look after import</p>
                </div>
                
                <div class="preview-container">
                    <div class="loading-spinner">
                        <i class="fas fa-spinner fa-spin fa-3x"></i>
                        <p>Processing data with AI...</p>
                    </div>
                </div>
                
                <div class="action-buttons mt-4">
                    <button class="btn btn-secondary" onclick="aiImportManager.navigateToStep('mapping')">
                        <i class="fas fa-arrow-left"></i> Back
                    </button>
                    <button class="btn btn-primary" onclick="aiImportManager.proceedToImport()">
                        Import Data <i class="fas fa-arrow-right"></i>
                    </button>
                </div>
            </div>
        `;
    }

    // Render validation step
    renderValidationStep() {
        return `
            <div class="import-step validation-step">
                <div class="step-header">
                    <h3>Data Validation</h3>
                    <p>AI is checking data quality and detecting duplicates</p>
                </div>
                
                <div class="validation-results">
                    <div class="loading-spinner">
                        <i class="fas fa-spinner fa-spin fa-3x"></i>
                        <p>Validating data...</p>
                    </div>
                </div>
            </div>
        `;
    }

    // Render complete step
    renderCompleteStep() {
        return `
            <div class="import-step complete-step">
                <div class="step-header">
                    <h3>Import Complete!</h3>
                </div>
                
                <div class="success-message">
                    <i class="fas fa-check-circle fa-5x text-success mb-3"></i>
                    <h4>Successfully imported data</h4>
                    <p>Your data has been processed and imported with AI assistance</p>
                </div>
                
                <div class="action-buttons mt-4">
                    <button class="btn btn-primary" onclick="location.href='/${this.importType}'">
                        View ${this.importType} <i class="fas fa-arrow-right"></i>
                    </button>
                    <button class="btn btn-secondary" onclick="aiImportManager.startNewImport()">
                        Import More Data
                    </button>
                </div>
            </div>
        `;
    }

    // Confirm mappings and proceed
    async confirmMappings() {
        // Collect user confirmations
        const selects = document.querySelectorAll('.mapping-select');
        selects.forEach(select => {
            const source = select.dataset.source;
            const target = select.value;
            if (target && target !== '_ignore') {
                this.mappingConfirmations[source] = target;
            }
        });

        // Proceed to import with mappings
        await this.processImportWithMappings();
    }

    // Process import with confirmed mappings
    async processImportWithMappings() {
        this.navigateToStep('preview');

        try {
            const response = await fetch('/api/import/process-ai', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    file_path: this.analysisData.file_path,
                    data_type: this.importType,
                    analysis: this.analysisData,
                    user_confirmations: this.mappingConfirmations
                })
            });

            const result = await response.json();

            if (result.success) {
                // Update preview with results
                this.updatePreviewWithResults(result.data);
            } else {
                this.showError(result.error || 'Failed to process import');
            }
        } catch (error) {
            this.showError('Processing failed: ' + error.message);
        }
    }

    // Update preview with processed results
    updatePreviewWithResults(data) {
        const container = document.querySelector('.preview-container');
        if (!container) return;

        const validation = data.validation_results || {};
        const duplicates = data.duplicate_info || {};

        container.innerHTML = `
            <div class="preview-results">
                <div class="data-quality-score mb-4">
                    <h5>Data Quality Score</h5>
                    <div class="progress">
                        <div class="progress-bar ${validation.data_quality_score >= 80 ? 'bg-success' : validation.data_quality_score >= 60 ? 'bg-warning' : 'bg-danger'}" 
                             style="width: ${validation.data_quality_score || 0}%">
                            ${validation.data_quality_score || 0}%
                        </div>
                    </div>
                </div>
                
                ${validation.total_issues > 0 ? `
                    <div class="validation-issues mb-4">
                        <h5><i class="fas fa-exclamation-triangle text-warning"></i> Issues Found</h5>
                        <ul class="issue-list">
                            ${validation.issues.map(issue => `
                                <li class="issue-item ${issue.severity}">
                                    <strong>${issue.field}:</strong> ${issue.issue}
                                    ${issue.affected_rows ? `(${issue.affected_rows} rows)` : ''}
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                ${duplicates.has_duplicates ? `
                    <div class="duplicate-warning mb-4">
                        <h5><i class="fas fa-copy text-info"></i> Potential Duplicates</h5>
                        <p>${duplicates.duplicate_count} potential duplicates found</p>
                    </div>
                ` : ''}
                
                <div class="import-summary">
                    <h5>Import Summary</h5>
                    <p><strong>${data.row_count}</strong> records ready to import</p>
                </div>
            </div>
        `;
    }

    // Helper functions
    formatSampleValues(values) {
        if (!values || values.length === 0) return '';
        return values.slice(0, 2).join(', ') + (values.length > 2 ? '...' : '');
    }

    showProgress(message) {
        // Show progress indicator
        const container = document.getElementById('importContainer');
        if (container) {
            container.innerHTML = `
                <div class="progress-message">
                    <i class="fas fa-spinner fa-spin fa-3x mb-3"></i>
                    <p>${message}</p>
                </div>
            `;
        }
    }

    showError(message) {
        // Show error message
        const container = document.getElementById('importContainer');
        if (container) {
            container.innerHTML = `
                <div class="error-message">
                    <i class="fas fa-exclamation-circle fa-3x text-danger mb-3"></i>
                    <p>${message}</p>
                    <button class="btn btn-primary mt-3" onclick="aiImportManager.startNewImport()">
                        Try Again
                    </button>
                </div>
            `;
        }
    }

    startNewImport() {
        this.currentStep = 'upload';
        this.analysisData = null;
        this.mappingConfirmations = {};
        this.fileInfo = null;
        this.renderCurrentStep();
    }

    attachStepHandlers() {
        // Attach any step-specific event handlers
    }
}

// Create global instance
const aiImportManager = new AIImportManager();