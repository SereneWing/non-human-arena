# 模板模块服务层

## 一、模板服务接口

```python
from typing import Protocol, List, Optional, Dict, Any, Callable

class ITemplateService(Protocol):
    """模板服务接口"""
    
    async def create(self, template: Template) -> Template:
        """创建模板"""
        ...
    
    async def get_by_id(self, template_id: str) -> Optional[Template]:
        """获取模板"""
        ...
    
    async def list_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        template_type: Optional[TemplateType] = None
    ) -> List[Template]:
        """列出所有模板"""
        ...
    
    async def update(self, template: Template) -> Template:
        """更新模板"""
        ...
    
    async def delete(self, template_id: str) -> bool:
        """删除模板"""
        ...
    
    async def render(
        self,
        template_id: str,
        variables: Dict[str, Any],
        strict: bool = True
    ) -> RenderResult:
        """渲染模板"""
        ...
    
    async def validate(
        self,
        content: str,
        variables: Dict[str, Any]
    ) -> List[str]:
        """验证模板"""
        ...
    
    async def search(
        self,
        query: str,
        template_type: Optional[TemplateType] = None
    ) -> List[Template]:
        """搜索模板"""
        ...
    
    async def duplicate(
        self,
        template_id: str,
        new_name: Optional[str] = None
    ) -> Template:
        """复制模板"""
        ...

class ITemplateRenderer(Protocol):
    """模板渲染器接口"""
    
    def render(
        self,
        template: Template,
        variables: Dict[str, Any]
    ) -> RenderResult:
        """渲染模板"""
        ...
    
    def extract_variables(self, content: str) -> List[str]:
        """提取变量"""
        ...
    
    def validate_syntax(self, content: str) -> List[str]:
        """验证语法"""
        ...
```

## 二、模板服务实现

```python
from jinja2 import Environment, BaseLoader, TemplateSyntaxError, UndefinedError
import re

class Jinja2TemplateRenderer:
    """Jinja2模板渲染器"""
    
    def __init__(self):
        self.env = Environment(loader=BaseLoader())
        self.env.filters['escape_json'] = self._escape_json
    
    def render(
        self,
        template: Template,
        variables: Dict[str, Any]
    ) -> RenderResult:
        """渲染模板"""
        errors = []
        warnings = []
        rendered_vars = {}
        
        try:
            # 合并变量
            merged_vars = {**template.default_values, **variables}
            
            # 编译模板
            compiled = self.env.from_string(template.content)
            
            # 渲染
            content = compiled.render(**merged_vars)
            
            # 记录渲染的变量
            for key in variables:
                if key in merged_vars:
                    rendered_vars[key] = merged_vars[key]
            
            return RenderResult(
                success=True,
                content=content,
                rendered_variables=rendered_vars,
                errors=errors,
                warnings=warnings
            )
            
        except TemplateSyntaxError as e:
            errors.append(f"模板语法错误: {e}")
            return RenderResult(
                success=False,
                content="",
                errors=errors,
                warnings=warnings
            )
            
        except UndefinedError as e:
            errors.append(f"未定义的变量: {e}")
            return RenderResult(
                success=False,
                content="",
                errors=errors,
                warnings=warnings
            )
    
    def extract_variables(self, content: str) -> List[str]:
        """提取变量"""
        pattern = r'\{\{\s*(\w+)(?:\.\w+)*\s*\}\}'
        matches = re.findall(pattern, content)
        return list(set(matches))
    
    def validate_syntax(self, content: str) -> List[str]:
        """验证语法"""
        errors = []
        try:
            self.env.from_string(content)
        except TemplateSyntaxError as e:
            errors.append(str(e))
        return errors
    
    @staticmethod
    def _escape_json(value):
        """JSON转义"""
        if isinstance(value, str):
            return value.replace('"', '\\"').replace('\n', '\\n')
        return value


class TemplateService:
    """模板服务"""
    
    def __init__(
        self,
        repository: ITemplateRepository,
        renderer: ITemplateRenderer
    ):
        self.repository = repository
        self.renderer = renderer
    
    async def create(self, template: Template) -> Template:
        """创建模板"""
        # 验证语法
        errors = self.renderer.validate_syntax(template.content)
        if errors:
            raise ValueError(f"模板语法错误: {errors}")
        
        # 自动提取变量
        extracted_vars = self.renderer.extract_variables(template.content)
        for var in extracted_vars:
            if var not in template.variables:
                template.variables.append(var)
        
        return await self.repository.create(template)
    
    async def render(
        self,
        template_id: str,
        variables: Dict[str, Any],
        strict: bool = True
    ) -> RenderResult:
        """渲染模板"""
        template = await self.repository.get_by_id(template_id)
        if not template:
            return RenderResult(
                success=False,
                content="",
                errors=[f"模板不存在: {template_id}"]
            )
        
        result = self.renderer.render(template, variables)
        
        if strict and not result.success:
            raise ValueError(f"渲染失败: {result.errors}")
        
        return result
    
    async def validate(
        self,
        content: str,
        variables: Dict[str, Any]
    ) -> List[str]:
        """验证模板"""
        errors = self.renderer.validate_syntax(content)
        
        # 检查必需的变量
        extracted = self.renderer.extract_variables(content)
        for var in extracted:
            if var not in variables and var not in content.split('{% if')[0]:
                errors.append(f"缺少变量: {var}")
        
        return errors
```

## 三、模板缓存

```python
from typing import Dict, Optional
import hashlib

class TemplateCache:
    """模板缓存"""
    
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self._cache: Dict[str, CompiledTemplate] = {}
        self._access_order: List[str] = []
    
    def get(self, template_id: str) -> Optional[Any]:
        """获取缓存的编译模板"""
        if template_id in self._cache:
            # 更新访问顺序
            self._access_order.remove(template_id)
            self._access_order.append(template_id)
            return self._cache[template_id].compiled
        return None
    
    def set(self, template_id: str, compiled: Any) -> None:
        """设置缓存"""
        if len(self._cache) >= self.max_size:
            # LRU淘汰
            oldest = self._access_order.pop(0)
            del self._cache[oldest]
        
        self._cache[template_id] = CompiledTemplate(compiled)
        self._access_order.append(template_id)
    
    def invalidate(self, template_id: str) -> None:
        """使缓存失效"""
        if template_id in self._cache:
            del self._cache[template_id]
            self._access_order.remove(template_id)
    
    def clear(self) -> None:
        """清空缓存"""
        self._cache.clear()
        self._access_order.clear()

@dataclass
class CompiledTemplate:
    """编译后的模板"""
    compiled: Any
    content_hash: str = ""
    
    @classmethod
    def create(cls, compiled: Any, content: str) -> "CompiledTemplate":
        return cls(
            compiled=compiled,
            content_hash=hashlib.md5(content.encode()).hexdigest()
        )
```
