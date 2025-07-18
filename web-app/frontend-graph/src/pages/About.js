import React from "react";
import "./About.css";  // Import CSS for styling

const About = () => {
  return (
    <div className="about-container">
      <h1>About the GAIJ Project</h1>

      <section className="about-section">
        <h2>Background</h2>
        <p>
          Illicit financial transactions constitute a serious ethical challenge to the proper 
          functioning of society. Various regulatory frameworks enforce banks, companies, and 
          governments to keep checks on illicit financial flows, yet in gross amount, these 
          still comprise a significant portion of the world's trade value.
        </p>
        <p>
          At the forefront of exposing malicious entities involved in non-sustainable activities 
          are investigative journalists. Yet assessing financial data in a digital world is a 
          strenuous task.
        </p>
        <p>
          <strong>GAIJ – Graph-bound Artificial Intelligence Journalism</strong> – is a project 
          centered on utilizing modern open-source Large Language Models (LLMs) to classify 
          illicit transactions in financial and tax records. The project will develop a 
          prototype open-source Artificial Intelligence (AI) model that examines and classifies 
          transaction data, creating a graph of suspicious interactions between companies.
        </p>
      </section>

      <section className="about-section">
        <h2>Aims</h2>
        <p>
          The working prototype, <strong>GAIJ – Graph-bound Artificial Intelligence Journalism</strong>, 
          is a project centered on utilizing open-source Large Language Models to classify 
          illicit transactions in financial and tax records.
        </p>
        <p>
          The target of this pilot project is to develop a prototype open-source, 
          Python-based AI model that examines and classifies transaction data and casts these 
          interactions onto a graph of interactions, used to trail suspicious activities by 
          financial agents.
        </p>
        <p>
          The project is developed at the intersection between **Artificial Intelligence 
          research and investigative journalism**. The primary goal is to develop a tool 
          that can help **journalists, academics, and the public** in identifying illicit 
          transactions of companies.
        </p>
      </section>
    </div>
  );
};

export default About;