"""
Business Rules Management System

This module handles loading, parsing, and managing business rules from YAML files.
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path
import yaml
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class BusinessRule:
    """Represents a single business rule"""
    id: str
    name: str
    description: str
    domain: str
    category: str
    condition: str
    action: str
    priority: int
    parameters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert rule to dictionary format"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "domain": self.domain,
            "category": self.category,
            "condition": self.condition,
            "action": self.action,
            "priority": self.priority,
            "parameters": self.parameters,
            "metadata": self.metadata
        }
    
    def to_text(self) -> str:
        """Convert rule to text format for embedding"""
        text_parts = [
            f"Domain: {self.domain}",
            f"Category: {self.category}",
            f"Rule: {self.name}",
            f"Description: {self.description}",
            f"Condition: {self.condition}",
            f"Action: {self.action}",
            f"Priority: {self.priority}"
        ]
        
        if self.parameters:
            params_text = ", ".join([f"{k}={v}" for k, v in self.parameters.items()])
            text_parts.append(f"Parameters: {params_text}")
            
        return " | ".join(text_parts)


class BusinessRulesManager:
    """Manages business rules loading and operations"""
    
    def __init__(self, rules_directory: Path):
        self.rules_directory = Path(rules_directory)
        self.rules: List[BusinessRule] = []
        self._rules_by_id: Dict[str, BusinessRule] = {}
        self._rules_by_domain: Dict[str, List[BusinessRule]] = {}
        
    def load_rules(self) -> None:
        """Load all business rules from YAML files"""
        if not self.rules_directory.exists():
            logger.error(f"Rules directory does not exist: {self.rules_directory}")
            return
            
        yaml_files = list(self.rules_directory.glob("*.yaml")) + list(self.rules_directory.glob("*.yml"))
        
        for yaml_file in yaml_files:
            try:
                self._load_rules_from_file(yaml_file)
                logger.info(f"Loaded rules from {yaml_file}")
            except Exception as e:
                logger.error(f"Error loading rules from {yaml_file}: {str(e)}")
                
        self._build_indices()
        logger.info(f"Loaded {len(self.rules)} business rules total")
    
    def _load_rules_from_file(self, file_path: Path) -> None:
        """Load rules from a single YAML file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            
        domain = data.get('domain', 'unknown')
        category = data.get('category', 'general')
        rules_data = data.get('rules', [])
        
        for rule_data in rules_data:
            try:
                rule = BusinessRule(
                    id=rule_data['id'],
                    name=rule_data['name'],
                    description=rule_data['description'],
                    domain=domain,
                    category=category,
                    condition=rule_data['condition'],
                    action=rule_data['action'],
                    priority=rule_data.get('priority', 1),
                    parameters=rule_data.get('parameters', {}),
                    metadata=rule_data.get('metadata', {})
                )
                self.rules.append(rule)
            except KeyError as e:
                logger.error(f"Missing required field {e} in rule: {rule_data}")
            except Exception as e:
                logger.error(f"Error creating rule: {str(e)}")
    
    def _build_indices(self) -> None:
        """Build internal indices for faster lookup"""
        self._rules_by_id.clear()
        self._rules_by_domain.clear()
        
        for rule in self.rules:
            self._rules_by_id[rule.id] = rule
            
            if rule.domain not in self._rules_by_domain:
                self._rules_by_domain[rule.domain] = []
            self._rules_by_domain[rule.domain].append(rule)
    
    def get_rule_by_id(self, rule_id: str) -> Optional[BusinessRule]:
        """Get a specific rule by its ID"""
        return self._rules_by_id.get(rule_id)
    
    def get_rules_by_domain(self, domain: str) -> List[BusinessRule]:
        """Get all rules for a specific domain"""
        return self._rules_by_domain.get(domain, [])
    
    def get_rules_by_category(self, category: str) -> List[BusinessRule]:
        """Get all rules for a specific category"""
        return [rule for rule in self.rules if rule.category == category]
    
    def get_all_rules(self) -> List[BusinessRule]:
        """Get all loaded rules"""
        return self.rules.copy()
    
    def get_rules_as_text(self) -> List[str]:
        """Get all rules as text strings for embedding"""
        return [rule.to_text() for rule in self.rules]
    
    def get_domains(self) -> List[str]:
        """Get list of all domains"""
        return list(self._rules_by_domain.keys())
    
    def get_categories(self) -> List[str]:
        """Get list of all categories"""
        categories = set(rule.category for rule in self.rules)
        return list(categories)
    
    def search_rules(self, query: str, domain: str = None, category: str = None) -> List[BusinessRule]:
        """Search rules by text query"""
        query_lower = query.lower()
        matching_rules = []
        
        for rule in self.rules:
            # Apply domain filter
            if domain and rule.domain != domain:
                continue
                
            # Apply category filter
            if category and rule.category != category:
                continue
            
            # Check if query matches rule text
            rule_text = rule.to_text().lower()
            if query_lower in rule_text:
                matching_rules.append(rule)
        
        # Sort by priority (higher priority first)
        matching_rules.sort(key=lambda r: r.priority, reverse=True)
        return matching_rules