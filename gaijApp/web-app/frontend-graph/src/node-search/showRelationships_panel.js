import React, { useState,useEffect  } from 'react';
import { useDispatch,useSelector } from 'react-redux';
import { buildRelationshipFilter } from '../backend-queries.js';
import { setPaths } from '../path-graph/actions.js';
import styles from './showRelationships_panel.module.css';

const Relationships = () => {
  const dispatch = useDispatch();
  // Get current filters from Redux store
  const relationshipFilters = useSelector(state => state.relationshipFilters);
  
  const [userSelections, setUserSelections] = useState({
    show_rels: {
      0: { question: 'located at', answer: true },
      1: { question: 'parent of', answer: true },
      2: { question: 'mentioned', answer: true },
      3: { question: 'auditor', answer: true }
    }
  });

  // Relationships available
  const relationships = [
    { id: 0, question: 'located at' },
    { id: 1, question: 'parent of' },
    { id: 2, question: 'mentioned' },
    { id: 3, question: 'auditor' }
  ];

  // Sync local state with Redux store when it changes
  useEffect(() => {
    if (relationshipFilters) {
      setUserSelections(relationshipFilters);
    }
  }, [relationshipFilters]);

  const handleCheckboxChange = (itemId, questionText, checked) => {
    const newSelections = {
      ...userSelections,
      show_rels: {
        ...userSelections.show_rels,
        [itemId]: {
          question: questionText,
          answer: checked
        }
      }
    };
    
    setUserSelections(newSelections);
    
    // Immediately dispatch to Redux store so SourceNode can use it
    dispatch(buildRelationshipFilter(newSelections));
  };

   const handleSelectAllCheckboxes = (checked) => {
    const newSelections = {
      ...userSelections,
      show_rels: relationships.reduce((acc, relationship) => ({
        ...acc,
        [relationship.id]: {
          question: relationship.question,
          answer: checked
        }
      }), {})
    };
    
    setUserSelections(newSelections);
    
    // Immediately dispatch to Redux store
    dispatch(buildRelationshipFilter(newSelections));
  };


  const handleSubmit = async () => {
    console.log('Current relationship filters:', userSelections);
    
    // Dispatch the current selections to Redux
    dispatch(buildRelationshipFilter(userSelections));
    
    // trigger a refresh of the graph here
    // dispatch an action to tell SourceNode to refresh
    // or use a custom event, etc.
  };



  return (
    <div className={styles.Filters}>
      <div className={styles.body}>
        <h3>Select relatonships to show</h3>
        <div className={styles.buttonPair}>
          <input
            type="checkbox"
            id="selectAll"
            onChange={(e) => handleSelectAllCheckboxes(e.target.checked)}
            checked={
              Object.values(userSelections.show_rels).length === relationships.length &&
              Object.values(userSelections.show_rels).every(item => item.answer)
            }
          />
          <label htmlFor="selectAll"><b>All relationships</b></label>
        </div>

        {relationships.map(item => (
          <div key={item.id} className={styles.checkboxRow}>
            <input
              type="checkbox"
              id={`question_${item.id}`}
              name={`question_${item.id}`}
              checked={!!userSelections.show_rels[item.id]?.answer}
              onChange={(e) =>
                handleCheckboxChange(item.id, item.question, e.target.checked)
              }
            />
            <label htmlFor={`question_${item.id}`}>{item.question}</label>
          </div>
        ))}


        <div className={styles.submit}>
          <button type="button" onClick={handleSubmit}>
            Show
          </button>
        </div>
      </div>
    </div>
  )
};

export default Relationships;