"""
GraphQL client for GitLab API
"""

import requests
import json
from typing import Optional, Dict, Any, List, Tuple
from config import Config

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class GraphQLClient:
    """Client for making GraphQL requests to GitLab"""
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize GraphQL client
        
        Args:
            config: Configuration object (uses default if not provided)
        """
        self.config = config or Config()
        self.url = self.config.graphql_url
        self.token = self.config.private_token
        self.ssl_verify = self.config.ssl_verify
    
    def make_request(self, query: str, variables: Optional[Dict] = None) -> Optional[Dict]:
        """
        Make an HTTP/JSON request to the GitLab GraphQL API endpoint
        
        Args:
            query: The GraphQL query string
            variables: Variables for the GraphQL query
            
        Returns:
            The JSON response from the GraphQL API or None on error
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
        
        payload = {
            "query": query,
            "variables": variables or {}
        }
        
        try:
            response = requests.post(
                self.url,
                headers=headers,
                data=json.dumps(payload),
                verify=self.ssl_verify
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"GraphQL request failed: {e}")
            return None


def get_issue_children(
    issue_id: int, 
    page_size: int = 50,
    end_cursor: str = ""
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Query child tasks of a specified issue using GraphQL
    
    Args:
        issue_id: The issue ID
        page_size: Number of results per page
        end_cursor: Pagination cursor
        
    Returns:
        Tuple of (main_status, list of child task dictionaries)
    """
    query = '''
    query workItemTreeQuery($id: WorkItemID!, $pageSize: Int = 100, $endCursor: String) {
      workItem(id: $id) {
        namespace {
          id
          fullName
          __typename
        }
        ...WorkItemHierarchy
        __typename
      }
    }

    fragment WorkItemHierarchy on WorkItem {
      id
      workItemType {
        id
        name
        iconName
        __typename
      }
      title
      confidential
      userPermissions {
        ...WorkItemPermissions
        __typename
      }
      widgets {
        type
        ... on WorkItemWidgetHierarchy {
          type
          hasChildren
          hasParent
          depthLimitReachedByType {
            workItemType {
              id
              name
              __typename
            }
            depthLimitReached
            __typename
          }
          rolledUpCountsByType {
            countsByState {
              opened
              all
              closed
              __typename
            }
            workItemType {
              id
              name
              iconName
              __typename
            }
            __typename
          }
          parent {
            id
            __typename
          }
          children(first: $pageSize, after: $endCursor) {
            pageInfo {
              ...PageInfo
              __typename
            }
            count
            nodes {
              id
              iid
              confidential
              workItemType {
                id
                name
                iconName
                __typename
              }
              namespace {
                id
                fullPath
                name
                __typename
              }
              title
              state
              createdAt
              closedAt
              webUrl
              reference(full: true)
              widgets {
                ... on WorkItemWidgetHierarchy {
                  type
                  hasChildren
                  rolledUpCountsByType {
                    countsByState {
                      all
                      closed
                      __typename
                    }
                    workItemType {
                      id
                      name
                      iconName
                      __typename
                    }
                    __typename
                  }
                  __typename
                }
                ...WorkItemMetadataWidgets
                __typename
              }
              __typename
            }
            __typename
          }
          __typename
        }
        ...WorkItemMetadataWidgets
        __typename
      }
      __typename
    }

    fragment PageInfo on PageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
      __typename
    }

    fragment WorkItemPermissions on WorkItemPermissions {
      adminParentLink
      adminWorkItemLink
      createNote
      deleteWorkItem
      markNoteAsInternal
      moveWorkItem
      reportSpam
      setWorkItemMetadata
      summarizeComments
      updateWorkItem
      blockedWorkItems
      __typename
    }

    fragment WorkItemMetadataWidgets on WorkItemWidget {
      type
      ... on WorkItemWidgetStartAndDueDate {
        dueDate
        startDate
        __typename
      }
      ... on WorkItemWidgetWeight {
        weight
        rolledUpWeight
        widgetDefinition {
          editable
          rollUp
          __typename
        }
        __typename
      }
      ... on WorkItemWidgetProgress {
        progress
        updatedAt
        __typename
      }
      ... on WorkItemWidgetHealthStatus {
        healthStatus
        rolledUpHealthStatus {
          count
          healthStatus
          __typename
        }
        __typename
      }
      ... on WorkItemWidgetMilestone {
        milestone {
          ...MilestoneFragment
          __typename
        }
        __typename
      }
      ... on WorkItemWidgetAssignees {
        allowsMultipleAssignees
        canInviteMembers
        assignees {
          nodes {
            ...User
            __typename
          }
          __typename
        }
        __typename
      }
      ... on WorkItemWidgetLabels {
        allowsScopedLabels
        labels {
          nodes {
            ...Label
            __typename
          }
          __typename
        }
        __typename
      }
      ... on WorkItemWidgetLinkedItems {
        blockedByCount
        blockingCount
        __typename
      }
      ... on WorkItemWidgetIteration {
        iteration {
          id
          title
          startDate
          dueDate
          webUrl
          iterationCadence {
            id
            title
            __typename
          }
          __typename
        }
        __typename
      }
      ... on WorkItemWidgetStatus {
        status {
          ...WorkItemStatusFragment
          __typename
        }
        __typename
      }
      __typename
    }

    fragment Label on Label {
      id
      title
      description
      color
      textColor
      __typename
    }

    fragment User on User {
      id
      avatarUrl
      name
      username
      webUrl
      webPath
      __typename
    }

    fragment MilestoneFragment on Milestone {
      expired
      id
      title
      state
      startDate
      dueDate
      webPath
      projectMilestone
      __typename
    }

    fragment WorkItemStatusFragment on WorkItemStatus {
      id
      category
      color
      description
      iconName
      name
      position
      __typename
    }
    '''
    
    client = GraphQLClient(Config())
    variables = {
        'id': f"gid://gitlab/WorkItem/{str(issue_id)}",
        "endCursor": end_cursor,
        "pageSize": page_size
    }
    
    result = client.make_request(query, variables)
    items = []
    main_status = ''
    
    if result and 'data' in result and 'workItem' in result['data']:
        work_item = result['data']['workItem']
        for widget in work_item.get('widgets', []):
            if widget.get('__typename') == 'WorkItemWidgetHierarchy':
                children = widget.get('children', {}).get('nodes', [])
                items = extract_child_task_details(children)
            elif widget.get('type') == 'STATUS':
                main_status = widget.get('status', {}).get('name', '')
    
    return main_status, items


def extract_child_task_details(children_nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Extract key information from child task nodes
    
    Args:
        children_nodes: List of child task nodes from GraphQL response
        
    Returns:
        List of dictionaries containing child task details
    """
    child_tasks = []
    
    for child in children_nodes:
        child_info = {
            'iid': child.get('iid'),
            'title': child.get('title'),
            'state': child.get('state'),
            'createdAt': child.get('createdAt'),
            'closedAt': child.get('closedAt'),
            'webUrl': child.get('webUrl'),
            'reference': child.get('reference'),
            'assignees': [],
            'labels': [],
            'status': '',
        }
        
        for widget in child.get('widgets', []):
            if widget.get('type') == 'ASSIGNEES':
                for node in widget.get('assignees', {}).get('nodes', []):
                    assignee = {
                        'name': node.get('name'),
                        'username': node.get('username'),
                        'webUrl': node.get('webUrl')
                    }
                    child_info['assignees'].append(assignee)
            
            elif widget.get('type') == 'LABELS':
                for node in widget.get('labels', {}).get('nodes', []):
                    label = {
                        'title': node.get('title'),
                        'description': node.get('description'),
                        'color': node.get('color')
                    }
                    child_info['labels'].append(label)
            elif widget.get('type') == 'STATUS':
                status_info = widget.get('status', {})
                child_info['status'] = status_info.get('name')
        
        child_tasks.append(child_info)
    
    return child_tasks
