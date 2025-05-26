// SelectionPanel.js
import React, { useState } from 'react';
import { useDispatch } from 'react-redux';
import styles from './SelectionPanel.module.css';
import { processUserSelection } from '../backend-queries.js';
import { setPaths } from '../path-graph/actions.js';

const SelectionPanel = ({ onSubmit }) => {
    const [userSelections, setUserSelections] = useState({
        info: 'external',
        nodeCount: 50,
        sortBy: 'TopCompaniesButton',
        reportMonth: { enabled: false, value: 'jan' },
        keyword: { enabled: false, value: 'none' },
        trueFalseAnswers: {}
    });
    const dispatch = useDispatch();

    const handleInputChange = (e) => {
        const { name, value, type, checked } = e.target;

        if (type === 'checkbox' && name === 'info') {
            setUserSelections(prev => ({
                ...prev,
                [name]: checked ? value : ''
            }));
        } else if (type === 'range') {
            setUserSelections(prev => ({
                ...prev,
                nodeCount: value
            }));
        } else if (name === 'show') {
            setUserSelections(prev => ({
                ...prev,
                sortBy: value
            }));
        }
    };

    const handleCheckboxDropdown = (e, dropdownId) => {
        const { checked } = e.target;
        const dropdown = document.getElementById(dropdownId);
        dropdown.disabled = !checked;
        if (!checked) dropdown.selectedIndex = 0;

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

    const handleRadioChange = (itemId, questionText, selectedAnswer) => {
        setUserSelections(prev => ({
            ...prev,
            trueFalseAnswers: {
                ...prev.trueFalseAnswers,
                [itemId]: {
                    question: questionText,
                    answer: selectedAnswer
                }
            }
        }));
    };

    
    const handleSubmit = async (e) => {
        e.preventDefault();

        if (onSubmit) {
            onSubmit(userSelections); // Your existing logic
        }

        console.log('Submitted selections:', userSelections);

        try {
            const graphData = await processUserSelection(userSelections);
            console.log('Graph Data:', graphData);
            
            if (graphData && graphData.nodes.length > 0) {
                const paths = graphData.edges.map((edge, index) => ({
                    node_ids: [edge.source_neo4j_id, edge.target_neo4j_id],
                    rel_ids: [index],
                    checked: true,
                    highlighted: false
                }));

                dispatch(
                    setPaths({
                        paths: paths,
                        nodes: graphData.nodes.reduce((acc, node) => {
                            acc[node.neo4j_id] = node;
                            return acc;
                        }, {}),
                        relationships: graphData.edges.reduce((acc, edge, index) => {
                            acc[index] = edge;
                            return acc;
                        }, {})
                    })
                );
            }
        } catch (error) {
            console.error('Error fetching graph data:', error);
        }
    };
   


    return (
        <div className={styles.selectionPanel}>
            <div className={styles.body}>
                <h3>Select input</h3>

                <div className={styles.selection}>
                    <div className={styles.radioInput}>
                        <label>
                            <input
                                type="checkbox"
                                name="info"
                                value="external"
                                checked={userSelections.info === 'external'}
                                onChange={handleInputChange}
                            />
                            External API
                        </label>

                        <label>
                            <input
                                type="checkbox"
                                name="info"
                                value="llm"
                                checked={userSelections.info === 'llm'}
                                onChange={handleInputChange}
                            />
                            Tax report (LLM)
                        </label>
                    </div>
                </div>

                <h3>Number of nodes</h3>
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

                <h3>Select one</h3>
                <div className={styles.radioGroup}>
                    <p><b>&nbsp;&nbsp;Sort by</b></p>

                    {[
                        { id: 't_sub', value: 'TopCompaniesButton', label: 'Companies with highest number of subsidiaries' },
                        { id: 't_bm', value: 'TopBoardMembersButton', label: 'Companies with highest number of board members' },
                        { id: 't_m', value: 'TopCompaniesMentionButton', label: 'Companies mentioned in most reports' },
                        { id: 't_a', value: 'TopAddressesButton', label: 'Addresses shared by most companies' },
                        { id: 't_au', value: 'TopAuditorButton', label: 'Auditor shared by most companies' },
                        { id: 't_c', value: 'SharedLeadershipButton', label: 'People leading most companies' },
                        { id: 't_p', value: 'TopPeopleMentionButton', label: 'People mentioned by most reports' }
                    ].map((radio) => (
                        <label key={radio.id}>
                            <input
                                type="radio"
                                name="show"
                                value={radio.value}
                                checked={userSelections.sortBy === radio.value}
                                onChange={handleInputChange}
                            />
                            {radio.label}
                        </label>
                    ))}

                    <p><b>&nbsp;&nbsp;Others</b></p>

                    {[
                        { id: 'sl', value: 'ParentSubsidiaryLeadershipButton', label: 'Parent subsidiary shared leadership' },
                        { id: 's2', value: 'CompaniesWithTwoSubsidiariesButton', label: 'Companies with two subsidiaries' }
                    ].map((radio) => (
                        <label key={radio.id}>
                            <input
                                type="radio"
                                name="show"
                                value={radio.value}
                                checked={userSelections.sortBy === radio.value}
                                onChange={handleInputChange}
                            />
                            {radio.label}
                        </label>
                    ))}
                </div>

                <h3>Filters</h3>

                <div className={styles.dateChoice}>
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
                                if (!e || !e.target) {
                                    console.error("Invalid event object", e);
                                    return;
                                }
                                const newValue = e.target.value;
                                if (!newValue) {
                                    console.error("Empty value received", e.target);
                                    return;
                                }
                                setUserSelections(prev => ({
                                    ...prev,
                                    reportMonth: {
                                        ...prev.reportMonth,
                                        value: newValue
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
                </div>

                <div className={styles.wordChoice}>
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
                                if (!e || !e.target) {
                                    console.error("Invalid event object", e);
                                    return;
                                }
                                const newValue = e.target.value;
                                if (!newValue) {
                                    console.error("Empty value received", e.target);
                                    return;
                                }
                                setUserSelections(prev => ({
                                    ...prev,
                                    keyword: {
                                        ...prev.keyword,
                                        value: newValue
                                    }
                                }))
                            }}
                        >
                            {[
                                'kompensasjon', 'sluttavtale', 'oppsigelsesdato',
                                'oppsigelse', 'sluttdato', 'opphør', 'trukket', 'etterlønn',
                                'bonus', 'variabel_lønn', 'resultatbasert', 'milepæl',
                                'etterbetaling', 'etterbetalt', 'privatlån', 'private_lån',
                                'selgerkreditt', 'interntransaksjon', 'diskresjonær',
                                'låneforfall', 'forfalt', 'ubetalt', 'solgt_aksjer',
                                'covid', 'covid-19', 'Kjell_Inge_Røkke'
                            ].map(word => (
                                <option key={word} value={word}>
                                    {word.replace('_', ' ')}
                                </option>
                            ))}
                        </select>
                    </label>
                </div>

                <div className={styles.header}>
                    <b>True&nbsp;&nbsp;&nbsp;False</b>
                </div>

                {[
                    { id: 0, question: 'Unclear or complicated financial instruments' },
                    { id: 1, question: 'Hidden leasing obligations' },
                    { id: 2, question: 'Guarantee obligations or pledges not clearly explained' },
                    { id: 3, question: 'Writing down values in the balance' },
                    { id: 4, question: 'Increasing dependence on financing to cover operations' },
                    { id: 5, question: 'Large one-off items or extraordinary income/costs' },
                    { id: 6, question: 'Internal transactions between group companies' },
                    { id: 7, question: 'Large outstanding receivables' },
                    { id: 8, question: 'The auditor expresses uncertainties or Going concerns' },
                    { id: 9, question: 'Changes in accounting principles' },
                    { id: 10, question: 'Adjustments to previous years accounts' },
                    { id: 11, question: 'Large deferred tax benefits' },
                    { id: 12, question: 'Abnormally low or outstanding tax payments' },
                    { id: 13, question: 'Lack of audit' },
                    { id: 14, question: 'Ongoing or potential litigation' },
                    { id: 15, question: 'Negative operational cash flows, while in profit' },
                    { id: 16, question: 'Large pension obligations' }
                ].map(item => (
                    <div key={item.id} className={styles.trueFalse}>
                        <div className={styles.question}>{item.question}</div>
                        <div className={styles.buttonPair} data-pair={item.id}>
                            <input
                                type="radio"
                                name={`question_${item.id}`}
                                value="true"
                                checked={userSelections.trueFalseAnswers[item.id]?.answer === 'true'}
                                onChange={(e) => handleRadioChange(item.id, item.question, e.target.value)}
                            />
                            <input
                                type="radio"
                                name={`question_${item.id}`}
                                value="false"
                                checked={userSelections.trueFalseAnswers[item.id]?.answer === 'false'}
                                onChange={(e) => handleRadioChange(item.id, item.question, e.target.value)}
                            />
                        </div>
                    </div>
                ))}

                <div className={styles.submit}>
                    <button type="button" onClick={handleSubmit}>Send Request</button>
                </div>
            </div>
        </div>
    );
};

export default SelectionPanel;





