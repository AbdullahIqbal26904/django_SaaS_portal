# Reseller/Partner Layer Implementation

This document explains the implementation of the reseller/partner layer functionality in the SaaS portal.

## Overview

The reseller/partner layer adds an abstraction between customers and the main service provider, allowing resellers/partners to sign up and manage their own customers under their account. These customers are billed and managed separately under the reseller.

## Key Components

1. **Reseller Model**: Represents partner organizations that can manage their own customers
2. **User Type**: Users can be either 'direct' or 'reseller' type
3. **Department Customer Type**: Departments can be either direct customers or reseller customers
4. **Subscription Source**: Subscriptions can be created directly or via a reseller

## Database Schema

The implementation adds the following models and relationships:

1. **Reseller**: Main entity for partner organizations
   - Fields: reseller_id, name, description, is_active, commission_rate, created_at, updated_at

2. **ResellerAdmin**: Links users to resellers as administrators
   - Fields: id, user (FK to User), reseller (FK to Reseller), assigned_at

3. **ResellerCustomer**: Links departments to resellers as customers
   - Fields: id, reseller (FK to Reseller), department (FK to Department), is_active, created_at

4. **Updates to User model**:
   - Added is_reseller_admin (boolean)
   - Added user_type field (choices: 'direct', 'reseller')

5. **Updates to Department model**:
   - Added customer_type field (choices: 'direct', 'reseller')

6. **Updates to Subscription model**:
   - Added subscription_source field (choices: 'direct', 'reseller')
   - Added reseller (FK to Reseller, nullable)

## Workflows

### Direct Customer Workflow

1. Customer registers directly on the platform
2. User is created with user_type='direct'
3. Departments created by this user are marked as customer_type='direct'
4. Subscriptions created for these departments have subscription_source='direct' and reseller=null

### Reseller Customer Workflow

1. Reseller admin registers a customer on the platform
2. User is created with user_type='reseller'
3. Department is created with customer_type='reseller'
4. Department is linked to the reseller via ResellerCustomer
5. Subscriptions created for these departments have subscription_source='reseller' and reseller set to the appropriate reseller

## API Endpoints

See [RESELLER_API_DOCUMENTATION.md](./RESELLER_API_DOCUMENTATION.md) for detailed API documentation.

## Permissions

The system implements different permission levels:

1. **Root Admin**: Can manage all resellers, departments, and subscriptions
2. **Reseller Admin**: Can manage customers and subscriptions under their reseller
3. **Department Admin**: Can manage their department's subscriptions
4. **Regular User**: Limited access based on their department and service access

## Future Enhancements

The following aspects are identified for future development:

1. **Billing & Packaging Logic**:
   - Different billing and pricing models for direct vs. reseller customers
   - Commission calculations for resellers
   - Bulk pricing for resellers

2. **Reseller Dashboard**:
   - Custom views and reports for resellers to manage their customers
   - Revenue and commission tracking

3. **White-labeling**:
   - Allow resellers to customize the interface for their customers
   - Custom branding and domain support
