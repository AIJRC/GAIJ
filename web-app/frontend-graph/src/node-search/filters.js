import React from 'react';
import { Component } from 'react';
import { connect } from 'react-redux';
import { faCheck } from '@fortawesome/free-solid-svg-icons';
import { faTimes } from '@fortawesome/free-solid-svg-icons';

import { Context } from './context.js';
import { IconButton } from '../utils/buttons';
import { Tooltip } from '../utils/tooltip';
import { FilterButton } from './filter-button.js';
import { compareObjects, copyObject } from '../utils/object';
import { makeFilenameFriendly, sortCustom, downloadCsv } from '../utils';

import './filters.css';

// filters component
export class Filters extends Component {
  // initialize component
  constructor() {
    super();

    this.state = {};
    this.state.filters = [];
    this.state.drag = null;
    this.state.dragList = [];
  }

  // when component mounts
  componentDidMount() {
    window.addEventListener('mouseup', this.onMouseUp);
  }

  // when component unmounts
  componentWillUnmount() {
    window.removeEventListener('mouseup', this.onMouseUp);
  }

  // when component updates
  componentDidUpdate(prevProps, prevState) {
    if (this.state.filters.length === 0 && this.props.metagraph.metanode_kinds)
      this.makeFilterList();

    if (!compareObjects(this.state.filters, prevState.filters))
      this.updateFilterString();
  }

  // make filter list based on metagraph metanode types
  makeFilterList = () => {
    let filters = [];
    for (const filter of this.props.metagraph.metanode_kinds)
      filters.push({ name: filter, active: true });

    // display filters in custom order
    const order = [
      'Gene',
      'Compound',
      'Anatomy',
      'Disease',
      'Symptom',
      'Side Effect',
      'Biological Process',
      'Cellular Component',
      'Molecular Function',
      'Pathway',
      'Pharmacolocic Class'
    ];
    filters = sortCustom(filters, order, 'name');

    this.setState({ filters: filters });
  };

  // assemble and update filter string for search query
  updateFilterString = () => {
    const list = [];
    for (const filter of this.state.filters) {
      if (filter.active)
        list.push(this.props.metagraph.kind_to_abbrev[filter.name]);
    }

    this.context.updateFilterString(list.join(','));
  };

  // toggle the specified filter on/off
  toggle = (name) => {
    const newFilters = copyObject(this.state.filters);

    for (const filter of newFilters) {
      if (filter.name === name)
        filter.active = !filter.active;
    }

    this.setState({ filters: newFilters });
  };

  // solo filter (turn all others off)
  solo = (name) => {
    let allOthersOff = true;

    for (const filter of this.state.filters) {
      if (filter.name !== name && filter.active) {
        allOthersOff = false;
        break;
      }
    }

    const newFilters = copyObject(this.state.filters);

    for (const filter of newFilters) {
      if (allOthersOff)
        filter.active = true;
      else {
        if (filter.name === name)
          filter.active = true;
        else
          filter.active = false;
      }
    }

    this.setState({ filters: newFilters });
  };

  // set the specified filter on/off
  set = (name, active) => {
    const newFilters = copyObject(this.state.filters);

    for (const filter of newFilters) {
      if (filter.name === name)
        filter.active = active;
    }

    this.setState({ filters: newFilters });
  };

  // make all filters active/inactive
  setAll = (active) => {
    const newFilters = copyObject(this.state.filters);

    for (const filter of newFilters)
      filter.active = active;

    this.setState({ filters: newFilters });
  };

  // when user releases mouse anywhere
  onMouseUp = (event) => {
    this.endDrag(event);
  };

  // begin dragging buttons
  beginDrag = (newActive) => {
    this.setState({ drag: newActive ? true : false });
  };

  // add row index to drag list
  addToDragList = (name) => {
    if (!this.state.dragList.includes(name))
      this.setState((state) => ({ dragList: [...state.dragList, name] }));
  };

  // end dragging buttons
  endDrag = () => {
    if (typeof this.state.drag !== 'boolean' || !this.state.dragList.length) {
      this.resetDrag();
      return;
    }

    const newFilters = copyObject(this.state.filters);

    for (const filter of newFilters) {
      if (this.state.dragList.includes(filter.name))
        filter.active = this.state.drag;
    }

    this.setState({ filters: newFilters });
    this.resetDrag();
  };

  // cancel dragging buttons
  resetDrag = () => {
    this.setState({ drag: null, dragList: [] });
  };

  // display component
  render() {
    const filterButtons = this.state.filters.map((filter, index) => (
      <FilterButton
        key={index}
        name={filter.name}
        tooltipText={this.props.tooltipDefinitions[filter.name]}
        active={filter.active}
        toggle={this.toggle}
        solo={this.solo}
        onMouseDown={this.onMouseDown}
        onMouseMove={this.onMouseMove}
        drag={this.state.drag}
        beginDrag={this.beginDrag}
        addToDragList={this.addToDragList}
      />
    ));

    return (
      <>
        <div className='node_search_filters'>
          <Tooltip
            text='Filter the text search by metanode.
              Ctrl+click to solo.'
          >
            <div className='small light'>Filters</div>
          </Tooltip>
          <div>
            <IconButton
              text='select all'
              icon={faCheck}
              onClick={() => this.setAll(true)}
            />
            <IconButton
              text='deselect all'
              icon={faTimes}
              onClick={() => this.setAll(false)}
            />
          </div>
          <div>{filterButtons}</div>
        </div>
      </>
    );
  }
}
// connect component to context component
Filters.contextType = Context;
// connect component to global state
Filters = connect((state) => ({
  metagraph: state.metagraph,
  tooltipDefinitions: state.tooltipDefinitions
}))(Filters);
