import React, { useState } from "react";
import "./Extend.css"; // Import CSS for styling

const Extend = () => {
  const [extensionType, setExtensionType] = useState("");
  const [newPropertyName, setNewPropertyName] = useState("");
  const [propertyDescription, setPropertyDescription] = useState("");
  const [selectedProperty, setSelectedProperty] = useState("");
  const [showTooltip, setShowTooltip] = useState(false); // Tooltip is now hidden by default

  return (
    <div className="extend-container">
      <h1>Extend the Graph - Dig Deeper</h1>
      <p>
        Our pipeline can also extract <strong>novel types of information</strong> from the dataset.
        By leveraging <strong>Large Language Models (LLMs)</strong>, we can <strong>query</strong> the data points 
        for any <strong>useful insights</strong> you wish to extract.
      </p>

      <form onSubmit={(e) => e.preventDefault()} className="extend-form">
        <label>Select the type of extension:</label>
        <select value={extensionType} onChange={(e) => setExtensionType(e.target.value)} required>
          <option value="">-- Select an option --</option>
          <option value="dig-deeper">Dig Deeper (New Property/Relationship)</option>
          <option value="fill-missing">Fill Missing Nodes with Properties</option>
        </select>

        {extensionType === "dig-deeper" && (
          <>
            <div className="input-with-tooltip">
              <label>Desired New Property Name:</label>

              {/* Info Button (i) */}
              <div
                className="info-button"
                onMouseEnter={() => setShowTooltip(true)}
                onMouseLeave={() => setTimeout(() => setShowTooltip(false), 300)}
              >
                ℹ
              </div>

              {/* Tooltip (Appears on Hover) */}
              {showTooltip && (
                <div
                  className="tooltip"
                  onMouseEnter={() => setShowTooltip(true)}
                  onMouseLeave={() => setShowTooltip(false)}
                >
                  <strong>Example:</strong> 
                  <br />
                  Desired New Property Name: Risk Score
                  <br />
                  Property Description: Risk Score is a categorical assessment of a company's financial, regulatory, or operational risks. It helps investors, regulators, and analysts evaluate how risky a company is regarding fraud, tax evasion, financial instability, or illicit activities. Tax records contain financial disclosures, deductions, and reported earnings. A Risk Score can be derived using data-driven techniques, such as: High offshore transactions, Tax-to-Revenue Ratio where a very low tax paid compared to revenue can indicate aggressive tax avoidance. Also check for statements related to undisclosed income or similar terms.
                  <br />
                  Please provide a classification for each company as "high" "medium" "low" or "unknown". 
                </div>
              )}
            </div>

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

        <button type="submit">Submit Request</button>
      </form>
    </div>
  );
};

export default Extend;
