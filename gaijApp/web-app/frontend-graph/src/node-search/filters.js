
import React, { useState } from 'react';
import { useDispatch } from 'react-redux';
import { get_userOptions,processUserSelection, get_userFilters } from '../backend-queries.js';
import { setPaths } from '../path-graph/actions.js';
import styles from './filters.module.css';


const FilterPanel = () => {
  const dispatch = useDispatch();


  const [selectedNodeTypeId, setSelectedNodeTypeId] = useState('');
  const [userSelections, setUserSelections] = useState({
    rel: 'all',
    show_rels: {},
    info: [], // allow multiple values for checkboxes
    nodeCount: 50,
    reportMonth: { enabled: false, value: 'jan' },
    keyword: { enabled: false, value: 'any' },
    nodeDisplayType: { enabled: false, value: 't_sub' },
    redFlag: { answer: false }
  });


  const nodeDisplayType = [
    { id: 't_sub', value: 'TopCompaniesButton', label: 'Companies with highest number of subsidiaries' },
    { id: 't_bm', value: 'TopBoardMembersButton', label: 'Companies with highest number of board members' },
    { id: 't_m', value: 'TopCompaniesMentionButton', label: 'Companies mentioned in most reports' },
    { id: 't_a', value: 'TopAddressesButton', label: 'Addresses shared by most companies' },
    { id: 't_au', value: 'TopAuditorButton', label: 'Auditor shared by most companies' },
    { id: 't_c', value: 'SharedLeadershipButton', label: 'People leading most companies' },
    { id: 't_p', value: 'TopPeopleMentionButton', label: 'People mentioned by most reports' },
    { id: 'sl', value: 'ParentSubsidiaryLeadershipButton', label: 'Parent subsidiary shared leadership' },
    { id: 's2', value: 'CompaniesWithTwoSubsidiariesButton', label: 'Companies with two subsidiaries' }
  ]

  const handleChange = (e) => {
    const newValue = e.target.value;
    setSelectedNodeTypeId(newValue);
    setUserSelections(prev => ({
      ...prev,
      nodeDisplayType: {
        ...prev.nodeDisplayType,
        value: newValue
      }
    }));
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;

    if (type === 'checkbox' && name === 'info') {
      setUserSelections(prev => {
        const infoArray = prev.info.includes(value)
          ? prev.info.filter(i => i !== value)
          : [...prev.info, value];
        return { ...prev, info: infoArray };
      });
    } else if (type === 'range') {
      setUserSelections(prev => ({ ...prev, nodeCount: value }));
    } else if (name === 'show') {
      setUserSelections(prev => ({ ...prev, sortBy: value }));
    }
  };

  const handleCheckboxDropdown = (e, dropdownId) => {
    const { checked } = e.target;
    const key = dropdownId === 'month' ? 'reportMonth' : 'keyword';
    const defaultValue = dropdownId === 'month' ? 'jan' : 'none';

    setUserSelections(prev => ({
      ...prev,
      [key]: {
        enabled: checked,
        value: checked ? prev[key].value : defaultValue
      }
    }));
  };


  // Relationships available
  const relationships = [
    { id: 0, question: 'located at' },
    { id: 1, question: 'parent of' },
    { id: 2, question: 'child of' },
    { id: 3, question: 'mentioned' },
    { id: 4, question: 'auditor' }
  ];

  const handleSelectAllCheckboxes = (checked) => {
    const newAnswers = {};
    relationships.forEach(item => {
      newAnswers[item.id] = {
        question: item.question,
        answer: checked
      };
    });
    setUserSelections(prev => ({
      ...prev,
      show_rels: newAnswers
    }));
  };

  const handleCheckboxChange = (itemId, questionText, checked) => {
    setUserSelections(prev => ({
      ...prev,
      show_rels: {
        ...prev.show_rels,
        [itemId]: {
          question: questionText,
          answer: checked
        }
      }
    }));
  };

  const handleSubmit = async () => {
    console.log(userSelections)
    const graphData = await get_userOptions(userSelections);
    if (graphData && graphData.nodes.length > 0) {
      const paths = graphData.edges.map((edge, index) => ({
        node_ids: [edge.source_neo4j_id, edge.target_neo4j_id],
        rel_ids: [index],
        checked: true,
        highlighted: false
      }));

      const formattedNodes = {};
      const formattedRelationships = {};
      graphData.nodes.forEach(node => {
        formattedNodes[node.neo4j_id] = node;
      });
      graphData.edges.forEach((edge, index) => {
        formattedRelationships[index] = edge;
      });

      dispatch(setPaths({
        paths,
        nodes: formattedNodes,
        relationships: formattedRelationships
      }));
    }
  };

  return (
    <div className={styles.Filters}>
      <div className={styles.body}>
        <div className={styles.threeColumnPanel}>

          <div className={styles.column}>
            <h3>Input</h3>
            <div className={styles.selection}>
              <div className={styles.radioInput}>
                <label>
                  <input
                    type="checkbox"
                    name="info"
                    value="external"
                    checked={userSelections.info.includes('external')}
                    onChange={handleInputChange}
                  />
                  External API
                </label>

                <label>
                  <input
                    type="checkbox"
                    name="info"
                    value="llm"
                    checked={userSelections.info.includes('llm')}
                    onChange={handleInputChange}
                  />
                  Tax report (LLM)
                </label>
              </div>
            </div>

            <p><b>&nbsp;&nbsp;Node number</b></p>
            <div className={styles.slider}>
              <input
                type="range"
                min="1"
                max="100"
                value={userSelections.nodeCount}
                onChange={handleInputChange}
              />
              <span>{userSelections.nodeCount}</span>
            </div>

            <label htmlFor="nodeSelect"><b>Select a node type </b>:</label>
            <select
              id="nodeSelect"
              value={selectedNodeTypeId}
              onChange={handleChange}
            >
              <option value="" disabled>Select an option</option>
              {nodeDisplayType.map((q) => (
                <option key={q.id} value={q.id}>
                  {q.label}
                </option>
              ))}
            </select>
          </div>



          <div className={styles.column}>
            <h3>Shown relationships</h3>
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
          </div>

          <div className={styles.column}>
            <h3>Filters</h3>

            <label>
              <input
                type="checkbox"
                onChange={(e) => handleCheckboxDropdown(e, 'month')}
              />
              Report delivery month
              <select
                id="month"
                disabled={!userSelections.reportMonth.enabled}
                value={userSelections.reportMonth.value}
                onChange={(e) => {
                  setUserSelections(prev => ({
                    ...prev,
                    reportMonth: {
                      ...prev.reportMonth,
                      value: e.target.value
                    }
                  }));
                }}
              >
                {['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'].map(month => (
                  <option key={month} value={month}>
                    {month.charAt(0).toUpperCase() + month.slice(1)}
                  </option>
                ))}
              </select>
            </label>

            <label>
              <input
                type="checkbox"
                onChange={(e) => handleCheckboxDropdown(e, 'words')}
              />
              Contains key word
              <select
                id="words"
                disabled={!userSelections.keyword.enabled}
                value={userSelections.keyword.value}
                onChange={(e) => {
                  setUserSelections(prev => ({
                    ...prev,
                    keyword: {
                      ...prev.keyword,
                      value: e.target.value
                    }
                  }))
                }}
              >
                {[
                  'any', 'kompensasjon', 'sluttavtale', 'oppsigelsesdato',
                  'oppsigelse', 'sluttdato', 'opphør', 'trukket', 'etterlønn',
                  'bonus', 'variabel lønn', 'resultatbasert', 'milepæl',
                  'etterbetaling', 'etterbetalt', 'privatlån', 'private lån',
                  'selgerkreditt', 'interntransaksjon', 'diskresjonær',
                  'låneforfall', 'forfalt', 'ubetalt', 'solgt aksjer',
                  'covid', 'covid-19', 'Kjell Inge Røkke'
                ].map(word => (
                  <option key={word} value={word}>
                    {word}
                  </option>
                ))}
              </select>
            </label>

            <div className={styles.buttonPair}>
              <input
                type="checkbox"
                id="redFlag"
                checked={!!userSelections.redFlag?.answer}
                onChange={(e) =>
                  setUserSelections(prev => ({
                    ...prev,
                    redFlag: { answer: e.target.checked }
                  }))
                }
              />
              <label htmlFor="redFlag">Red Flags</label>
            </div>
          </div>
        </div>

        <div className={styles.submit}>
          <button type="button" onClick={handleSubmit}>
            Show
          </button>
        </div>
      </div>
    </div>
  );
};

export default FilterPanel;
