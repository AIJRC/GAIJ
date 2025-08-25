import React from 'react';
import { Component } from 'react';

import { MetanodeChip } from '../components/chips.js';
// import { ReactComponent as PathIcon } from '../images/path.svg';

import './dropdown.css';

// dropdown sub-component of search box component
class Dropdown extends Component {
  render() {
    return (
      <div className='node_search_menu' {...this.props.getMenuProps()}>
        {this.props.isOpen && (
          <>
            {this.props.searchResults.map((result, index) => (
              <div
                className={
                  'node_search_item' +
                  (this.props.selectedItem.id === result.id ||
                  this.props.highlightedIndex === index ?
                    ' node_search_item_selected' :
                    '')
                }
                {...this.props.getItemProps({
                  item: result,
                  key: index
                })}
              >
                <MetanodeChip type={result.metanode} />
                <span className='node_search_name nowrap'>
                  {this.props.nodeType === 'Tax Number' ? result.properties.id : result.name}
                </span>
              </div>
            ))}
            {this.props.hasMore && (
              <div 
                className='node_search_item load-more'
                onClick={this.props.onLoadMore}
              >
                {this.props.isLoading ? 'Loading...' : 'Load more results...'}
              </div>
            )}
          </>
        )}
      </div>
    );
  }
}

export {Dropdown}