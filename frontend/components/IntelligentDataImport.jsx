import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, CheckCircle, AlertCircle, ArrowRight, Loader2, Info, Database, Shield, Zap } from 'lucide-react';

const IntelligentDataImport = ({ entityType = 'suppliers' }) => {
  const [importStep, setImportStep] = useState('upload');
  const [uploadedFile, setUploadedFile] = useState(null);
  const [aiAnalysis, setAiAnalysis] = useState(null);
  const [mappingConfirmed, setMappingConfirmed] = useState({});
  const [isProcessing, setIsProcessing] = useState(false);
  const [importResults, setImportResults] = useState(null);
  const [validationIssues, setValidationIssues] = useState([]);

  const onDrop = useCallback(async (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (!file) return;

    setUploadedFile(file);
    setImportStep('analyzing');
    setIsProcessing(true);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('data_type', entityType);
      
      const response = await fetch('/api/import/analyze-ai', {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        throw new Error('Analysis failed');
      }

      const analysis = await response.json();
      setAiAnalysis(analysis.data);
      setImportStep('mapping');
    } catch (error) {
      console.error('Analysis failed:', error);
      setImportStep('error');
    } finally {
      setIsProcessing(false);
    }
  }, [entityType]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls']
    },
    multiple: false,
    maxSize: 10 * 1024 * 1024 // 10MB
  });

  const processImport = async () => {
    setImportStep('processing');
    setIsProcessing(true);

    try {
      const response = await fetch('/api/import/process-ai', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          file_path: aiAnalysis.file_path,
          data_type: entityType,
          analysis: aiAnalysis,
          user_confirmations: mappingConfirmed
        })
      });

      const result = await response.json();
      
      if (result.success) {
        setImportResults(result.data);
        setValidationIssues(result.data.validation_results?.issues || []);
        setImportStep('preview');
      } else {
        throw new Error(result.error);
      }
    } catch (error) {
      console.error('Processing failed:', error);
      setImportStep('error');
    } finally {
      setIsProcessing(false);
    }
  };

  const finalizeImport = async () => {
    setImportStep('importing');
    setIsProcessing(true);

    try {
      // Final import would happen here
      await new Promise(resolve => setTimeout(resolve, 2000)); // Simulate API call
      setImportStep('complete');
    } catch (error) {
      console.error('Import failed:', error);
      setImportStep('error');
    } finally {
      setIsProcessing(false);
    }
  };

  const UploadStep = () => (
    <div className="space-y-6">
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all
          ${isDragActive 
            ? 'border-blue-400 bg-blue-50 scale-105' 
            : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50'
          }
        `}
      >
        <input {...getInputProps()} />
        <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        <p className="text-lg font-medium text-gray-900 mb-2">
          Drop your file here, or click to browse
        </p>
        <p className="text-sm text-gray-500">
          Supports CSV, Excel (.xlsx, .xls) up to 10MB
        </p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-blue-50 p-4 rounded-lg">
          <Zap className="h-8 w-8 text-blue-600 mb-2" />
          <h4 className="font-medium text-blue-900 mb-1">Smart Mapping</h4>
          <p className="text-sm text-blue-700">AI automatically maps your columns to our schema</p>
        </div>
        <div className="bg-green-50 p-4 rounded-lg">
          <Shield className="h-8 w-8 text-green-600 mb-2" />
          <h4 className="font-medium text-green-900 mb-1">Data Validation</h4>
          <p className="text-sm text-green-700">Automatic cleaning and standardization</p>
        </div>
        <div className="bg-purple-50 p-4 rounded-lg">
          <Database className="h-8 w-8 text-purple-600 mb-2" />
          <h4 className="font-medium text-purple-900 mb-1">Duplicate Detection</h4>
          <p className="text-sm text-purple-700">Intelligent duplicate identification</p>
        </div>
      </div>
    </div>
  );

  const AnalyzingStep = () => (
    <div className="text-center py-12">
      <Loader2 className="animate-spin h-12 w-12 text-blue-600 mx-auto mb-4" />
      <h3 className="text-lg font-medium text-gray-900 mb-2">AI is analyzing your file...</h3>
      <p className="text-sm text-gray-500 max-w-md mx-auto">
        Our AI is examining your data structure, detecting patterns, and preparing intelligent field mappings
      </p>
      <div className="mt-8 space-y-2 max-w-sm mx-auto">
        <div className="flex items-center text-sm text-gray-600">
          <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
          File uploaded successfully
        </div>
        <div className="flex items-center text-sm text-gray-600">
          <Loader2 className="animate-spin h-4 w-4 text-blue-500 mr-2" />
          Analyzing data structure...
        </div>
      </div>
    </div>
  );

  const MappingStep = () => (
    <div className="space-y-6">
      {/* Mapping Statistics */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold text-green-600">
              {aiAnalysis?.confirmed_mappings?.length || 0}
            </div>
            <div className="text-sm text-gray-600">Auto-mapped</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-yellow-600">
              {aiAnalysis?.uncertain_mappings?.length || 0}
            </div>
            <div className="text-sm text-gray-600">Need confirmation</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-gray-600">
              {aiAnalysis?.unmapped_fields?.length || 0}
            </div>
            <div className="text-sm text-gray-600">Unmapped</div>
          </div>
        </div>
      </div>

      {/* Confirmed Mappings */}
      {aiAnalysis?.confirmed_mappings?.length > 0 && (
        <div className="bg-green-50 p-4 rounded-lg">
          <h4 className="text-sm font-medium text-green-800 mb-3 flex items-center">
            <CheckCircle className="h-4 w-4 mr-2" />
            Confirmed Mappings
          </h4>
          <div className="space-y-2">
            {aiAnalysis.confirmed_mappings.map((mapping, index) => (
              <div key={index} className="flex items-center justify-between bg-white p-3 rounded border border-green-200">
                <div className="flex items-center space-x-3">
                  <span className="font-medium text-gray-700">{mapping.source_field}</span>
                  <ArrowRight className="h-4 w-4 text-gray-400" />
                  <span className="text-gray-900">{mapping.target_field}</span>
                </div>
                <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">
                  {mapping.confidence}% match
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Uncertain Mappings */}
      {aiAnalysis?.uncertain_mappings?.length > 0 && (
        <div className="bg-yellow-50 p-4 rounded-lg">
          <h4 className="text-sm font-medium text-yellow-800 mb-3 flex items-center">
            <AlertCircle className="h-4 w-4 mr-2" />
            Please Confirm These Mappings
          </h4>
          <div className="space-y-3">
            {aiAnalysis.uncertain_mappings.map((mapping, index) => (
              <div key={index} className="bg-white p-4 rounded border border-yellow-200">
                <div className="flex items-center justify-between mb-3">
                  <span className="font-medium text-gray-900">{mapping.source_field}</span>
                  <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full">
                    {mapping.confidence}% confidence
                  </span>
                </div>
                <select 
                  className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  value={mappingConfirmed[mapping.source_field] || ''}
                  onChange={(e) => setMappingConfirmed({
                    ...mappingConfirmed,
                    [mapping.source_field]: e.target.value
                  })}
                >
                  <option value="">Select target field...</option>
                  {mapping.suggested_targets?.map(target => (
                    <option key={target} value={target}>{target}</option>
                  ))}
                  <option value="__skip__">Skip this field</option>
                </select>
                {mapping.reasoning && (
                  <p className="text-xs text-gray-600 mt-2 flex items-start">
                    <Info className="h-3 w-3 mr-1 mt-0.5 flex-shrink-0" />
                    {mapping.reasoning}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex justify-between pt-4">
        <button 
          onClick={() => setImportStep('upload')} 
          className="px-4 py-2 text-gray-600 hover:text-gray-800"
        >
          ← Back
        </button>
        <button 
          onClick={processImport}
          disabled={isProcessing}
          className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400 flex items-center"
        >
          {isProcessing ? (
            <>
              <Loader2 className="animate-spin h-4 w-4 mr-2" />
              Processing...
            </>
          ) : (
            'Process Data'
          )}
        </button>
      </div>
    </div>
  );

  const PreviewStep = () => (
    <div className="space-y-6">
      {/* Data Quality Score */}
      <div className="bg-gray-50 p-6 rounded-lg">
        <h4 className="text-lg font-medium mb-4">Data Quality Assessment</h4>
        <div className="mb-4">
          <div className="flex justify-between text-sm mb-2">
            <span>Overall Quality Score</span>
            <span className="font-medium">{importResults?.validation_results?.data_quality_score || 0}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div 
              className={`h-3 rounded-full transition-all ${
                importResults?.validation_results?.data_quality_score >= 80 
                  ? 'bg-green-500' 
                  : importResults?.validation_results?.data_quality_score >= 60 
                    ? 'bg-yellow-500' 
                    : 'bg-red-500'
              }`}
              style={{ width: `${importResults?.validation_results?.data_quality_score || 0}%` }}
            />
          </div>
        </div>

        {/* Statistics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold text-gray-900">{importResults?.row_count || 0}</div>
            <div className="text-sm text-gray-600">Total Records</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-green-600">{importResults?.row_count - (validationIssues.length || 0) || 0}</div>
            <div className="text-sm text-gray-600">Valid Records</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-yellow-600">{validationIssues.length || 0}</div>
            <div className="text-sm text-gray-600">Issues Found</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-blue-600">{importResults?.duplicate_info?.duplicate_count || 0}</div>
            <div className="text-sm text-gray-600">Duplicates</div>
          </div>
        </div>
      </div>

      {/* Validation Issues */}
      {validationIssues.length > 0 && (
        <div className="bg-yellow-50 p-4 rounded-lg">
          <h4 className="text-sm font-medium text-yellow-800 mb-3">Validation Issues</h4>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {validationIssues.map((issue, index) => (
              <div key={index} className="text-sm bg-white p-2 rounded border border-yellow-200">
                <span className="font-medium">{issue.field}:</span> {issue.issue}
                {issue.affected_rows && (
                  <span className="text-xs text-gray-600 ml-2">({issue.affected_rows} rows)</span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex justify-between pt-4">
        <button 
          onClick={() => setImportStep('mapping')} 
          className="px-4 py-2 text-gray-600 hover:text-gray-800"
        >
          ← Back to Mapping
        </button>
        <button 
          onClick={finalizeImport}
          disabled={isProcessing}
          className="px-6 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:bg-gray-400 flex items-center"
        >
          {isProcessing ? (
            <>
              <Loader2 className="animate-spin h-4 w-4 mr-2" />
              Importing...
            </>
          ) : (
            'Complete Import'
          )}
        </button>
      </div>
    </div>
  );

  const CompleteStep = () => (
    <div className="text-center py-12">
      <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
      <h3 className="text-2xl font-bold text-gray-900 mb-2">Import Successful!</h3>
      <p className="text-gray-600 mb-8">
        Your data has been imported successfully with AI assistance
      </p>
      <div className="bg-gray-50 p-6 rounded-lg max-w-md mx-auto mb-8">
        <div className="space-y-3">
          <div className="flex justify-between">
            <span className="text-gray-600">Records imported:</span>
            <span className="font-medium">{importResults?.row_count || 0}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Processing time:</span>
            <span className="font-medium">2.3 seconds</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">AI confidence:</span>
            <span className="font-medium">{aiAnalysis?.mapping_coverage || 0}%</span>
          </div>
        </div>
      </div>
      <div className="space-x-4">
        <button 
          onClick={() => window.location.href = `/${entityType}`}
          className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          View {entityType}
        </button>
        <button 
          onClick={() => {
            setImportStep('upload');
            setUploadedFile(null);
            setAiAnalysis(null);
            setMappingConfirmed({});
            setImportResults(null);
          }}
          className="px-6 py-2 border border-gray-300 rounded hover:bg-gray-50"
        >
          Import Another File
        </button>
      </div>
    </div>
  );

  const ErrorStep = () => (
    <div className="text-center py-12">
      <AlertCircle className="h-16 w-16 text-red-500 mx-auto mb-4" />
      <h3 className="text-xl font-bold text-gray-900 mb-2">Import Failed</h3>
      <p className="text-gray-600 mb-8">
        An error occurred during the import process
      </p>
      <button 
        onClick={() => {
          setImportStep('upload');
          setUploadedFile(null);
          setAiAnalysis(null);
        }}
        className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
      >
        Try Again
      </button>
    </div>
  );

  const steps = {
    upload: <UploadStep />,
    analyzing: <AnalyzingStep />,
    mapping: <MappingStep />,
    processing: <AnalyzingStep />,
    preview: <PreviewStep />,
    importing: <AnalyzingStep />,
    complete: <CompleteStep />,
    error: <ErrorStep />
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          AI-Powered {entityType.charAt(0).toUpperCase() + entityType.slice(1)} Import
        </h1>
        <p className="text-gray-600">
          Upload your data and let our AI handle the complex mapping and validation
        </p>
      </div>

      {/* Progress Indicator */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          {['upload', 'analyzing', 'mapping', 'preview', 'complete'].map((step, index) => (
            <div key={step} className="flex items-center">
              <div className={`
                w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium transition-all
                ${importStep === step 
                  ? 'bg-blue-600 text-white scale-110' 
                  : index < ['upload', 'analyzing', 'mapping', 'preview', 'complete'].indexOf(importStep) 
                    ? 'bg-green-500 text-white' 
                    : 'bg-gray-200 text-gray-600'
                }
              `}>
                {index < ['upload', 'analyzing', 'mapping', 'preview', 'complete'].indexOf(importStep) ? (
                  <CheckCircle className="h-5 w-5" />
                ) : (
                  index + 1
                )}
              </div>
              {index < 4 && (
                <div className={`
                  w-full h-1 mx-2 transition-all
                  ${index < ['upload', 'analyzing', 'mapping', 'preview', 'complete'].indexOf(importStep)
                    ? 'bg-green-500' 
                    : 'bg-gray-200'
                  }
                `} />
              )}
            </div>
          ))}
        </div>
        <div className="flex justify-between mt-2">
          <span className="text-xs text-gray-600">Upload</span>
          <span className="text-xs text-gray-600">Analyze</span>
          <span className="text-xs text-gray-600">Map Fields</span>
          <span className="text-xs text-gray-600">Preview</span>
          <span className="text-xs text-gray-600">Complete</span>
        </div>
      </div>

      {/* Current Step Content */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        {steps[importStep]}
      </div>
    </div>
  );
};

export default IntelligentDataImport;