# 命名規則ガイド

## Python

| 対象 | 規則 | 例 |
|------|------|-----|
| 変数 | snake_case | `user_name`, `total_count` |
| 関数 | snake_case | `calculate_total()`, `get_user_by_id()` |
| クラス | PascalCase | `UserService`, `OrderRepository` |
| 定数 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT`, `DEFAULT_TIMEOUT` |
| プライベート | _prefix | `_internal_cache`, `_validate()` |
| モジュール | snake_case | `user_service.py`, `data_loader.py` |

## TypeScript / JavaScript

| 対象 | 規則 | 例 |
|------|------|-----|
| 変数 | camelCase | `userName`, `totalCount` |
| 関数 | camelCase | `calculateTotal()`, `getUserById()` |
| クラス | PascalCase | `UserService`, `OrderRepository` |
| インターフェース | PascalCase (I prefix不要) | `UserProfile`, `ApiResponse` |
| 定数 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| Enum | PascalCase | `UserRole.Admin` |
| React コンポーネント | PascalCase | `UserCard`, `OrderList` |

## 共通ルール

- **略語は避ける**: `usr` → `user`, `mgr` → `manager`
- **ブーリアン変数**: `is_`, `has_`, `can_` プレフィックス → `is_active`, `has_permission`
- **コレクション**: 複数形を使う → `users`, `order_items`
- **関数名は動詞で始める**: `get_`, `create_`, `update_`, `delete_`, `validate_`, `calculate_`
