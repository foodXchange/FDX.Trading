/**
 * Enhanced Product Analysis JavaScript
 * Handles GPT-4 Vision data with confidence scores and multilingual support
 */

// Enhanced form population function with GPT-4 Vision support
function autoPopulateFormWithData(data) {
    // Handle different data sources (GPT-4 Vision vs traditional analysis)
    const brief = data.brief || {};
    const analysis = data.analysis && data.analysis.length > 0 ? data.analysis[0] : {};
    
    // Check if this is GPT-4 Vision analysis
    const isGPT4Vision = analysis.analysis_method === 'gpt-4-vision' || analysis.gpt4v_analysis;
    const gpt4vData = analysis.gpt4v_analysis || {};
    
    // Populate Product Identity with confidence indicators
    document.getElementById('productName').value = brief.product_name || gpt4vData.product_name || '';
    updateConfidenceIndicator('productNameConfidence', gpt4vData.confidence_scores?.overall || 0.95);
    
    // Handle multilingual product names
    if (gpt4vData.product_name_hebrew || brief.product_name_hebrew) {
        // Add Hebrew name as a tooltip or additional field
        const productNameField = document.getElementById('productName');
        productNameField.setAttribute('data-hebrew', gpt4vData.product_name_hebrew || brief.product_name_hebrew);
        productNameField.setAttribute('title', `Hebrew: ${gpt4vData.product_name_hebrew || brief.product_name_hebrew}`);
    }
    
    document.getElementById('brandName').value = brief.brand_name || gpt4vData.brand_name || '';
    updateConfidenceIndicator('brandNameConfidence', calculateFieldConfidence('brand', gpt4vData));
    
    document.getElementById('productCategory').value = brief.category || gpt4vData.category || '';
    updateConfidenceIndicator('categoryConfidence', calculateFieldConfidence('category', gpt4vData));
    
    document.getElementById('packageSize').value = brief.package_size || gpt4vData.package_size || '';
    updateConfidenceIndicator('packageSizeConfidence', calculateFieldConfidence('package_size', gpt4vData));
    
    // Populate Basic Description
    document.getElementById('productType').value = brief.product_type || gpt4vData.product_type || '';
    document.getElementById('mainIngredients').value = brief.main_ingredients || gpt4vData.main_ingredients || '';
    document.getElementById('flavorProfile').value = brief.flavor_profile || gpt4vData.flavor_profile || '';
    document.getElementById('targetGroup').value = brief.target_group || gpt4vData.target_group || '';
    
    // Populate Special Characteristics with enhanced kosher handling
    const kosherStatus = brief.kosher_status || gpt4vData.kosher_status || 'Unknown';
    document.getElementById('kosherStatus').value = kosherStatus;
    updateConfidenceIndicator('kosherConfidence', calculateFieldConfidence('kosher', gpt4vData));
    
    // Show Hebrew kosher text if available
    if (gpt4vData.kosher_text_hebrew) {
        const kosherField = document.getElementById('kosherStatus');
        kosherField.setAttribute('data-hebrew', gpt4vData.kosher_text_hebrew);
        kosherField.setAttribute('title', `Hebrew: ${gpt4vData.kosher_text_hebrew}`);
    }
    
    document.getElementById('healthClaims').value = brief.health_claims || gpt4vData.health_claims || '';
    document.getElementById('allergenWarnings').value = brief.allergen_warnings || gpt4vData.allergen_warnings || '';
    
    // Handle dietary features checkboxes with multilingual support
    const dietaryFeatures = brief.dietary_features || gpt4vData.dietary_features || [];
    document.getElementById('glutenFree').checked = dietaryFeatures.some(f => 
        f.includes('Gluten-Free') || f.includes('ללא גלוטן')
    );
    document.getElementById('organic').checked = dietaryFeatures.some(f => 
        f.includes('Organic') || f.includes('אורגני')
    );
    document.getElementById('vegan').checked = dietaryFeatures.some(f => 
        f.includes('Vegan') || f.includes('טבעוני')
    );
    document.getElementById('nonGmo').checked = dietaryFeatures.some(f => 
        f.includes('Non-GMO')
    );
    
    // Populate Nutritional Facts
    document.getElementById('caloriesPerServing').value = brief.calories_per_serving || gpt4vData.calories_per_serving || '';
    document.getElementById('servingSize').value = brief.serving_size || gpt4vData.serving_size || '';
    document.getElementById('keyNutrients').value = brief.key_nutrients || gpt4vData.key_nutrients || '';
    
    // Populate AI Analysis Meta
    const overallConfidence = gpt4vData.confidence_scores?.overall || analysis.confidence_score || 0.8;
    document.getElementById('confidenceLevel').value = Math.round(overallConfidence * 100);
    document.getElementById('confidenceValue').textContent = Math.round(overallConfidence * 100) + '%';
    
    const textQuality = gpt4vData.confidence_scores?.text_quality || brief.text_quality || 'Clear';
    document.getElementById('textQuality').value = textQuality;
    
    const analysisStatus = gpt4vData.confidence_scores?.analysis_status || brief.analysis_status || 'Complete';
    document.getElementById('analysisStatus').value = analysisStatus;
    
    // Update AI suggestions based on confidence scores
    updateAISuggestions(gpt4vData.confidence_scores || {});
    
    // Update review items based on low confidence fields
    updateReviewItems(gpt4vData);
    
    // If multilingual text was found, show language indicators
    if (gpt4vData.detected_languages && gpt4vData.detected_languages.length > 1) {
        showMultilingualIndicator(gpt4vData.detected_languages);
    }
}

function updateConfidenceIndicator(elementId, confidence) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const percentage = Math.round(confidence * 100);
    element.textContent = `${percentage}%`;
    
    // Update color based on confidence level
    element.classList.remove('high', 'medium', 'low');
    if (percentage >= 80) {
        element.classList.add('high');
    } else if (percentage >= 60) {
        element.classList.add('medium');
    } else {
        element.classList.add('low');
    }
}

function calculateFieldConfidence(fieldName, gpt4vData) {
    // If we have specific field confidence, use it
    if (gpt4vData.field_confidences && gpt4vData.field_confidences[fieldName]) {
        return gpt4vData.field_confidences[fieldName];
    }
    
    // Otherwise estimate based on whether field has value and overall confidence
    const hasValue = gpt4vData[fieldName] && gpt4vData[fieldName] !== '';
    const overallConfidence = gpt4vData.confidence_scores?.overall || 0.8;
    
    // Field-specific adjustments
    const fieldAdjustments = {
        'kosher': hasValue ? 0.9 : 0.45, // Lower confidence for kosher if not detected
        'brand': hasValue ? 0.85 : 0.75,
        'category': 0.9, // Usually high confidence
        'package_size': hasValue ? 0.88 : 0.7
    };
    
    return fieldAdjustments[fieldName] || (hasValue ? overallConfidence : overallConfidence * 0.7);
}

function updateAISuggestions(confidenceScores) {
    const suggestionsContainer = document.querySelector('.card-body');
    if (!suggestionsContainer) return;
    
    let suggestionsHtml = '';
    
    // Check overall confidence
    const overall = confidenceScores.overall || 0.8;
    if (overall >= 0.8) {
        suggestionsHtml += `
            <div class="suggestion-item mb-2">
                <i class="fas fa-check-circle text-success me-2"></i>
                <small>High confidence analysis (${Math.round(overall * 100)}%)</small>
            </div>
        `;
    }
    
    // Check text quality
    if (confidenceScores.text_quality === 'clear') {
        suggestionsHtml += `
            <div class="suggestion-item mb-2">
                <i class="fas fa-check-circle text-success me-2"></i>
                <small>Text quality is clear</small>
            </div>
        `;
    } else if (confidenceScores.text_quality === 'partial') {
        suggestionsHtml += `
            <div class="suggestion-item mb-2">
                <i class="fas fa-exclamation-triangle text-warning me-2"></i>
                <small>Some text may be unclear</small>
            </div>
        `;
    }
    
    // Check Hebrew recognition
    if (confidenceScores.hebrew_recognition && confidenceScores.hebrew_recognition < 0.7) {
        suggestionsHtml += `
            <div class="suggestion-item mb-2">
                <i class="fas fa-exclamation-triangle text-warning me-2"></i>
                <small>Hebrew text recognition needs review</small>
            </div>
        `;
    }
    
    // Update suggestions if container found
    const suggestionsCard = document.querySelector('.card-header:has(.fa-info-circle)')?.parentElement;
    if (suggestionsCard) {
        const cardBody = suggestionsCard.querySelector('.card-body');
        if (cardBody && suggestionsHtml) {
            cardBody.innerHTML = suggestionsHtml;
        }
    }
}

function updateReviewItems(gpt4vData) {
    const reviewContainer = document.querySelector('#needReviewCard .card-body');
    if (!reviewContainer) return;
    
    let reviewHtml = '';
    const fieldsToReview = [];
    
    // Check each field's confidence
    const fieldConfidences = {
        'Product Name': calculateFieldConfidence('product_name', gpt4vData),
        'Brand': calculateFieldConfidence('brand', gpt4vData),
        'Kosher Status': calculateFieldConfidence('kosher', gpt4vData),
        'Package Size': calculateFieldConfidence('package_size', gpt4vData)
    };
    
    // Add fields with low confidence to review
    for (const [field, confidence] of Object.entries(fieldConfidences)) {
        if (confidence < 0.7) {
            fieldsToReview.push({ field, confidence });
        }
    }
    
    // Sort by confidence (lowest first)
    fieldsToReview.sort((a, b) => a.confidence - b.confidence);
    
    // Generate review HTML
    fieldsToReview.forEach(item => {
        reviewHtml += `
            <div class="review-item mb-2">
                <i class="fas fa-exclamation-triangle text-warning me-2"></i>
                <small>${item.field} (${Math.round(item.confidence * 100)}%)</small>
            </div>
        `;
    });
    
    // Add general review item if needed
    if (gpt4vData.confidence_scores?.analysis_status === 'needs_review') {
        reviewHtml += `
            <div class="review-item">
                <i class="fas fa-info-circle text-info me-2"></i>
                <small>Manual review recommended</small>
            </div>
        `;
    }
    
    if (reviewHtml) {
        reviewContainer.innerHTML = reviewHtml;
    }
}

function showMultilingualIndicator(languages) {
    // Show indicator that multiple languages were detected
    const languageMap = {
        'he': 'Hebrew',
        'en': 'English',
        'ar': 'Arabic',
        'ru': 'Russian',
        'fr': 'French',
        'es': 'Spanish'
    };
    
    const detectedLangs = languages.map(l => languageMap[l] || l).join(', ');
    showNotification(`Multiple languages detected: ${detectedLangs}`, 'info');
    
    // Add visual indicator to the form
    const langIndicator = document.createElement('div');
    langIndicator.className = 'alert alert-info mt-2';
    langIndicator.innerHTML = `
        <i class="fas fa-language me-2"></i>
        <strong>Multilingual Product:</strong> ${detectedLangs}
    `;
    
    // Add to the form if not already present
    const existingIndicator = document.querySelector('.multilingual-indicator');
    if (!existingIndicator) {
        const analysisCard = document.getElementById('analysisCard');
        if (analysisCard) {
            const cardBody = analysisCard.querySelector('.card-body');
            if (cardBody) {
                langIndicator.classList.add('multilingual-indicator');
                cardBody.insertBefore(langIndicator, cardBody.firstChild);
            }
        }
    }
}

// Helper function to collect all form data
function collectFormData() {
    const dietaryFeatures = [];
    if (document.getElementById('glutenFree').checked) dietaryFeatures.push('Gluten-Free');
    if (document.getElementById('organic').checked) dietaryFeatures.push('Organic');
    if (document.getElementById('vegan').checked) dietaryFeatures.push('Vegan');
    if (document.getElementById('nonGmo').checked) dietaryFeatures.push('Non-GMO');
    
    return {
        // Product Identity
        productName: document.getElementById('productName').value,
        brandName: document.getElementById('brandName').value,
        productCategory: document.getElementById('productCategory').value,
        packageSize: document.getElementById('packageSize').value,
        
        // Product Details
        productType: document.getElementById('productType').value,
        mainIngredients: document.getElementById('mainIngredients').value,
        flavorProfile: document.getElementById('flavorProfile').value,
        targetGroup: document.getElementById('targetGroup').value,
        
        // Special Characteristics
        kosherStatus: document.getElementById('kosherStatus').value,
        dietaryFeatures: dietaryFeatures,
        healthClaims: document.getElementById('healthClaims').value,
        allergenWarnings: document.getElementById('allergenWarnings').value,
        
        // Nutritional Facts
        caloriesPerServing: document.getElementById('caloriesPerServing').value,
        servingSize: document.getElementById('servingSize').value,
        keyNutrients: document.getElementById('keyNutrients').value,
        
        // AI Analysis Meta
        confidenceLevel: document.getElementById('confidenceLevel').value,
        textQuality: document.getElementById('textQuality').value,
        analysisStatus: document.getElementById('analysisStatus').value
    };
}

// Auto-populate button functionality
function autoPopulateFields() {
    if (currentAnalysisData) {
        autoPopulateFormWithData(currentAnalysisData);
        showNotification('Fields auto-populated with AI analysis', 'success');
    } else {
        showNotification('No analysis data available', 'warning');
    }
}

// Save as draft functionality
function saveAsDraft() {
    const formData = collectFormData();
    localStorage.setItem('draftAnalysis', JSON.stringify({
        data: formData,
        timestamp: new Date().toISOString()
    }));
    showNotification('Analysis saved as draft', 'success');
}

// Reset form functionality
function resetForm() {
    if (confirm('Are you sure you want to reset all fields?')) {
        document.getElementById('productAnalysisForm')?.reset();
        // Reset confidence indicators
        document.querySelectorAll('.confidence-indicator').forEach(el => {
            el.textContent = '0%';
            el.classList.remove('high', 'medium', 'low');
        });
        showNotification('Form reset successfully', 'info');
    }
}

// Add verification reminder banner
function addVerificationReminder() {
    // Check if reminder already exists
    if (document.getElementById('verificationReminder')) {
        return;
    }
    
    // Create reminder banner
    const reminderHtml = `
        <div id="verificationReminder" class="alert alert-warning alert-dismissible fade show mb-4" role="alert">
            <div class="d-flex align-items-start">
                <i class="fas fa-exclamation-triangle me-3 mt-1"></i>
                <div class="flex-grow-1">
                    <h6 class="alert-heading mb-2">AI Analysis Complete - Verification Required</h6>
                    <p class="mb-2">The AI has populated the form based on the product image analysis. Please:</p>
                    <ul class="mb-2">
                        <li>Review all auto-filled fields carefully</li>
                        <li>Pay special attention to fields with low confidence scores (marked in yellow/red)</li>
                        <li>Verify Hebrew text and kosher certifications are correctly identified</li>
                        <li>Edit any incorrect information directly in the form fields</li>
                        <li>Check that all allergen warnings are properly captured</li>
                    </ul>
                    <small class="text-muted">AI analysis may contain errors. Human verification is essential for accuracy.</small>
                </div>
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        </div>
    `;
    
    // Insert at the top of the analysis form
    const analysisCard = document.getElementById('analysisCard');
    if (analysisCard) {
        analysisCard.insertAdjacentHTML('beforebegin', reminderHtml);
        
        // Auto-scroll to the reminder
        document.getElementById('verificationReminder').scrollIntoView({ 
            behavior: 'smooth', 
            block: 'nearest' 
        });
    }
}

// Export the enhanced function to replace the existing one
if (typeof window !== 'undefined') {
    window.autoPopulateFormWithData = autoPopulateFormWithData;
    window.updateConfidenceIndicator = updateConfidenceIndicator;
    window.calculateFieldConfidence = calculateFieldConfidence;
    window.updateAISuggestions = updateAISuggestions;
    window.updateReviewItems = updateReviewItems;
    window.showMultilingualIndicator = showMultilingualIndicator;
    window.collectFormData = collectFormData;
    window.autoPopulateFields = autoPopulateFields;
    window.saveAsDraft = saveAsDraft;
    window.resetForm = resetForm;
    window.addVerificationReminder = addVerificationReminder;
}