import React from 'react';
import { Component } from 'react';
import Downshift from 'downshift';
import { connect } from 'react-redux';
import { setPaths } from '../path-graph/actions.js';

import { Context } from './context.js';
// import { Tooltip } from '../utils/tooltip';
import { TextBox } from './text-box.js';
import { Dropdown } from './dropdown.js';
import { searchNodes, fetchNodeConnections } from '../backend-queries.js';

import './search-box.css';

const NODES_PER_PAGE = 1000;

// search box component with dropdown autocomplete/autosuggest
export class SearchBox extends Component {
  // initialize component
  constructor(props) {
    super(props);
    this.state = {
      searchResults: [],
      selectedItem: null,
      page: 1,
      hasMore: true,
      isLoading: false
    };
    this.inputRef = React.createRef();
  }

  handleSelection = (selectedItem) => {
    if (selectedItem) {
      this.setState({ selectedItem });
      this.props.onChange(selectedItem);
    } else {
      // When clearing or toggling visibility, ensure paths structure is valid
      this.setState({ selectedItem: null });
      this.props.dispatch(
        setPaths({
          paths: [],
          nodes: {},
          relationships: {}
        })
      );
      this.props.onChange(null);
    }
  };

  // Add itemToString method
  itemToString = (item) => {
    if (!item) return '';
    return item.name || '';
  };

  filterNodesWithConnections = async (nodes) => {
    const validResults = [];
    for (const result of nodes) {
      const nodeId = result.neo4j_id || result.id || result.properties?.id;
      if (!nodeId) continue;

      try {
        const connections = await fetchNodeConnections(
          nodeId,
          this.props.nodeType === 'Tax Number' ? 'Company' : this.props.nodeType
        );

        // More strict validation of connections
        if (connections?.edges?.some(edge => 
          edge && 
          edge.source_neo4j_id && 
          edge.target_neo4j_id && 
          (edge.source_neo4j_id === nodeId || edge.target_neo4j_id === nodeId)
        )) {
          validResults.push({
            ...result,
            neo4j_id: nodeId,
            id: nodeId,
            elementType: 'node',
            connections: connections
          });
        }
      } catch (error) {
        console.error(`Error checking connections for node ${nodeId}:`, error);
      }
    }
    return validResults;
  };

  onInput = async (searchString) => {
    if (searchString === undefined) return;
    
    this.setState({ isLoading: true, page: 1 });

    try {
      const results = await searchNodes(
        searchString || '',
        this.props.nodeType === 'Tax Number' ? 'id' : '',
        this.props.nodeType === 'Tax Number' ? 'Company' : this.props.nodeType || 'Person',
        this.props.nodeType === 'Tax Number',
        1,
        NODES_PER_PAGE
      );

      if (!results || results.length === 0) {
        this.setState({ searchResults: [], hasMore: false, isLoading: false });
        return;
      }

      // Filter out nodes without connections
      const validResults = await this.filterNodesWithConnections(results);

      this.setState({ 
        searchResults: this.props.nodeType === 'Tax Number' 
          ? validResults.sort((a, b) => Number(a.id) - Number(b.id))
          : validResults,
        hasMore: results.length === NODES_PER_PAGE,
        isLoading: false
      });

      return validResults[0];
    } catch (error) {
      console.error('Error during search:', error);
      this.setState({ searchResults: [], hasMore: false, isLoading: false });
    }
  };

  loadMore = async () => {
    if (this.state.isLoading || !this.state.hasMore) return;

    const nextPage = this.state.page + 1;
    this.setState({ isLoading: true });

    try {
      const results = await searchNodes(
        this.inputRef.current?.value || '',
        this.props.nodeType === 'Tax Number' ? 'id' : '',
        this.props.nodeType === 'Tax Number' ? 'Company' : this.props.nodeType || 'Person',
        this.props.nodeType === 'Tax Number',
        nextPage,
        NODES_PER_PAGE
      );

      if (!results || results.length === 0) {
        this.setState({ hasMore: false, isLoading: false });
        return;
      }

      const validResults = await this.filterNodesWithConnections(results);
      
      this.setState(prevState => ({ 
        searchResults: [...prevState.searchResults, ...validResults],
        page: nextPage,
        hasMore: results.length === NODES_PER_PAGE,
        isLoading: false
      }));
    } catch (error) {
      console.error('Error loading more results:', error);
      this.setState({ isLoading: false });
    }
  };

  // Modify itemToString to show ID for Tax Number searches
  itemToString = (item) => {
    if (!item) return '';
    return this.props.nodeType === 'Tax Number' ? item.id : item.name;
  };

  render() {
    return (
      <div className='node_search_form'>
        <Downshift
          onChange={this.handleSelection}
          itemToString={this.itemToString}
          selectedItem={this.state.selectedItem}
        >
          {({
            getInputProps,
            getItemProps,
            getMenuProps,
            isOpen,
            inputValue,
            selectedItem,
            highlightedIndex,
            clearSelection,
            openMenu,
            closeMenu
          }) => (
            <div className="search-box-container">
              <TextBox
                getInputProps={getInputProps}
                selectedItem={selectedItem}
                clearSelection={clearSelection}
                openMenu={openMenu}
                closeMenu={closeMenu}
                onFocus={this.onInput}
                inputRef={this.inputRef}
                nodeType={this.props.nodeType}  // Pass nodeType to TextBox
              />
              <Dropdown
                isOpen={isOpen}
                searchResults={this.state.searchResults}
                getMenuProps={getMenuProps}
                getItemProps={getItemProps}
                selectedItem={selectedItem || {}}
                highlightedIndex={highlightedIndex}
                nodeType={this.props.nodeType}  // Add this line
              />
            </div>
          )}
        </Downshift>
      </div>
    );
  }
}

SearchBox = connect()(SearchBox);
SearchBox.contextType = Context;
