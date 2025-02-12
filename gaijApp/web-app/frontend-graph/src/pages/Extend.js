import React, { useState } from "react";
import "./Extend.css"; // Import CSS for styling

const Extend = () => {
  const [extensionType, setExtensionType] = useState(""); // Stores user selection
  const [selectedFile, setSelectedFile] = useState(null);
  const [manualSelection, setManualSelection] = useState("");
  const [newPropertyName, setNewPropertyName] = useState("");
  const [propertyDescription, setPropertyDescription] = useState("");
  const [selectedProperty, setSelectedProperty] = useState("");

  // Example list of existing properties (this can be fetched dynamically)
  const existingProperties = ["Location", "Revenue", "Industry", "Ownership"];

  // Handles file selection
  const handleFileUpload = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  // Handles form submission
  const handleSubmit = (event) => {
    event.preventDefault();

    // Prepare data
    const requestData = {
      extensionType,
      selectedFile: selectedFile ? selectedFile.name : null,
      manualSelection,
      extraInfo: extensionType === "dig-deeper" ? { newPropertyName, propertyDescription } : selectedProperty,
    };

    console.log("Submitted Data:", requestData);
    alert("Request submitted successfully!");
  };

  return (
    <div className="extend-container">
      <h1>Extend the Graph - Dig Deeper</h1>
      <p>
        Our pipeline can also extract <strong>novel types of information</strong> from the dataset.
        By leveraging <strong>Large Language Models (LLMs)</strong>, we can <strong>query</strong> the data points 
        for any <strong>useful insights</strong> you wish to extract.
      </p>

      <form onSubmit={handleSubmit} className="extend-form">
        {/* Extension Type Selection */}
        <label>Select the type of extension:</label>
        <select value={extensionType} onChange={(e) => setExtensionType(e.target.value)} required>
          <option value="">-- Select an option --</option>
          <option value="dig-deeper">Dig Deeper (New Property/Relationship)</option>
          <option value="fill-missing">Fill Missing Nodes with Properties</option>
        </select>

        {/* Data Selection - Side-by-Side */}
        <label>Select the dataset subset to extend:</label>
        <div className="data-selection">
          <input
            type="text"
            value={manualSelection}
            onChange={(e) => setManualSelection(e.target.value)}
            placeholder="Manually enter or search company IDs"
          />
          <span>OR</span>
          <input type="file" accept=".csv" onChange={handleFileUpload} />
        </div>

        {/* Fields for Dig Deeper */}
        {extensionType === "dig-deeper" && (
          <>
            <label>Desired New Property Name:</label>
            <input
              type="text"
              value={newPropertyName}
              onChange={(e) => setNewPropertyName(e.target.value)}
              placeholder="Enter new property name"
              required
            />

            <label>Property Description:</label>
            <p className="description-helper">
              Please describe this new property with as much detail as possible.  
              Also, add some example results you expect to find in the dataset.  
              Specify what values to add when that property is not found for each data point.
            </p>
            <textarea
              value={propertyDescription}
              onChange={(e) => setPropertyDescription(e.target.value)}
              required
            />
          </>
        )}

        {/* Fields for Filling Missing Nodes */}
        {extensionType === "fill-missing" && (
          <>
            <label>Select an existing property to fill in missing nodes:</label>
            <select value={selectedProperty} onChange={(e) => setSelectedProperty(e.target.value)} required>
              <option value="">-- Select a property --</option>
              {existingProperties.map((prop, index) => (
                <option key={index} value={prop}>{prop}</option>
              ))}
            </select>
          </>
        )}

        {/* Submit Button */}
        <button type="submit">Submit Request</button>
      </form>
    </div>
  );
};

export default Extend;