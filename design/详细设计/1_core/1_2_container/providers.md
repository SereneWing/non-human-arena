# 依赖注入配置

## 一、概述

使用依赖注入容器管理模块依赖，实现控制反转，提高代码可测试性和可维护性。

## 二、Provider 类型

```python
from enum import Enum
from typing import Type, TypeVar, Callable, Any

T = TypeVar('T')

class ProviderScope(Enum):
    """作用域"""
    SINGLETON = "singleton"       # 单例（整个应用生命周期）
    SESSION = "session"         # 会话级（会话生命周期）
    TRANSIENT = "transient"     # 瞬态（每次请求创建新实例）
    REQUEST = "request"         # 请求级（每个请求创建新实例）

class Provider(ABC, Generic[T]):
    """提供者抽象基类"""
    
    @abstractmethod
    def get(self) -> T:
        """获取实例"""
        pass
    
    @abstractmethod
    def dispose(self, instance: T) -> None:
        """释放实例"""
        pass

class SingletonProvider(Provider[T]):
    """单例提供者"""
    
    def __init__(self, factory: Callable[[], T]):
        self._factory = factory
        self._instance: Optional[T] = None
    
    def get(self) -> T:
        if self._instance is None:
            self._instance = self._factory()
        return self._instance
    
    def dispose(self, instance: T) -> None:
        if hasattr(instance, 'dispose'):
            instance.dispose()

class TransientProvider(Provider[T]):
    """瞬态提供者"""
    
    def __init__(self, factory: Callable[[], T]):
        self._factory = factory
    
    def get(self) -> T:
        return self._factory()
    
    def dispose(self, instance: T) -> None:
        if hasattr(instance, 'dispose'):
            instance.dispose()

class SessionProvider(Provider[T]):
    """会话级提供者"""
    
    def __init__(self, factory: Callable[[], T]):
        self._factory = factory
        self._instances: Dict[str, T] = {}
    
    def get(self, session_id: Optional[str] = None) -> T:
        if session_id is None:
            return self._factory()
        
        if session_id not in self._instances:
            self._instances[session_id] = self._factory()
        return self._instances[session_id]
    
    def dispose_session(self, session_id: str) -> None:
        if session_id in self._instances:
            instance = self._instances.pop(session_id)
            self.dispose(instance)
    
    def dispose(self, instance: T) -> None:
        if hasattr(instance, 'dispose'):
            instance.dispose()
```

## 三、容器配置

```python
class Container:
    """依赖注入容器"""
    
    def __init__(self):
        self._providers: Dict[Type, Provider] = {}
        self._factories: Dict[Type, Callable] = {}
        self._scopes: Dict[Type, ProviderScope] = {}
        self._parent: Optional['Container'] = None
    
    # ==================== 注册 ====================
    
    def register(
        self,
        interface: Type[T],
        implementation: Type[T],
        scope: ProviderScope = ProviderScope.TRANSIENT,
        **kwargs
    ) -> 'Container':
        """注册类型映射"""
        def factory():
            return self._create_instance(implementation, **kwargs)
        
        self._providers[interface] = self._create_provider(factory, scope)
        self._factories[interface] = factory
        self._scopes[interface] = scope
        return self
    
    def register_instance(
        self,
        interface: Type[T],
        instance: T
    ) -> 'Container':
        """注册实例（单例）"""
        self._providers[interface] = SingletonProvider(lambda: instance)
        return self
    
    def register_factory(
        self,
        interface: Type[T],
        factory: Callable[[], T],
        scope: ProviderScope = ProviderScope.TRANSIENT
    ) -> 'Container':
        """注册工厂函数"""
        self._providers[interface] = self._create_provider(factory, scope)
        self._factories[interface] = factory
        self._scopes[interface] = scope
        return self
    
    # ==================== 解析 ====================
    
    def resolve(self, interface: Type[T]) -> T:
        """解析依赖"""
        if interface in self._providers:
            return self._providers[interface].get()
        
        # 尝试自动注入
        if interface not in self._factories:
            self._providers[interface] = self._create_provider_from_type(interface)
        
        return self._providers[interface].get()
    
    def resolve_with_session(self, interface: Type[T], session_id: str) -> T:
        """解析会话级依赖"""
        if interface not in self._providers:
            raise KeyError(f"未注册的依赖: {interface}")
        
        provider = self._providers[interface]
        if isinstance(provider, SessionProvider):
            return provider.get(session_id)
        return provider.get()
    
    # ==================== 生命周期 ====================
    
    def create_child(self) -> 'Container':
        """创建子容器"""
        child = Container()
        child._parent = self
        return child
    
    def clear_session(self, session_id: str) -> None:
        """清理会话级依赖"""
        for interface, provider in self._providers.items():
            if isinstance(provider, SessionProvider):
                provider.dispose_session(session_id)
    
    def clear(self) -> None:
        """清理所有依赖"""
        for provider in self._providers.values():
            if isinstance(provider, SingletonProvider):
                provider.dispose(None)
        self._providers.clear()
    
    # ==================== 内部方法 ====================
    
    def _create_provider(
        self,
        factory: Callable[[], T],
        scope: ProviderScope
    ) -> Provider[T]:
        """创建提供者"""
        if scope == ProviderScope.SINGLETON:
            return SingletonProvider(factory)
        elif scope == ProviderScope.SESSION:
            return SessionProvider(factory)
        else:
            return TransientProvider(factory)
    
    def _create_provider_from_type(self, cls: Type[T]) -> Provider[T]:
        """从类型创建提供者"""
        def factory():
            return self._create_instance(cls)
        return TransientProvider(factory)
    
    def _create_instance(self, cls: Type, **kwargs) -> Any:
        """创建实例（自动注入依赖）"""
        # 获取构造函数参数
        sig = inspect.signature(cls.__init__)
        params = {}
        
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            if param_name in kwargs:
                params[param_name] = kwargs[param_name]
            elif param.annotation in self._providers:
                params[param_name] = self.resolve(param.annotation)
        
        return cls(**params)
```

## 四、系统服务注册

```python
def configure_providers(container: Container) -> None:
    """配置系统服务"""
    
    # ==================== 核心服务 ====================
    
    # 配置
    container.register_instance(Config, config)
    
    # 日志
    container.register(
        LoggerInterface,
        Logger,
        scope=ProviderScope.SINGLETON
    )
    
    # 数据库
    container.register(
        Database,
        DatabaseImpl,
        scope=ProviderScope.SINGLETON
    )
    
    # ==================== 事件总线 ====================
    
    container.register(
        EventBus,
        LocalEventBus,
        scope=ProviderScope.SINGLETON
    )
    
    # ==================== 仓储 ====================
    
    container.register(
        RoleRepository,
        RoleRepositoryImpl,
        scope=ProviderScope.SINGLETON
    )
    
    container.register(
        SessionRepository,
        SessionRepositoryImpl,
        scope=ProviderScope.SINGLETON
    )
    
    container.register(
        RuleRepository,
        RuleRepositoryImpl,
        scope=ProviderScope.SINGLETON
    )
    
    container.register(
        HistoryRepository,
        HistoryRepositoryImpl,
        scope=ProviderScope.SINGLETON
    )
    
    # ==================== 引擎 ====================
    
    container.register(
        RuleEngine,
        RuleEngineImpl,
        scope=ProviderScope.SESSION
    )
    
    container.register(
        AIEngine,
        AIEngineImpl,
        scope=ProviderScope.SESSION
    )
    
    container.register(
        LLMClient,
        OpenAIClient,
        scope=ProviderScope.SINGLETON
    )
    
    # ==================== 模块 ====================
    
    container.register(
        RoleModule,
        RoleModuleImpl,
        scope=ProviderScope.SINGLETON
    )
    
    container.register(
        SessionModule,
        SessionModuleImpl,
        scope=ProviderScope.SESSION
    )
    
    container.register(
        HistoryModule,
        HistoryModuleImpl,
        scope=ProviderScope.SINGLETON
    )
    
    container.register(
        HeartbeatEngine,
        HeartbeatEngineImpl,
        scope=ProviderScope.SINGLETON
    )
```

## 五、装饰器支持

```python
def injectable(
    scope: ProviderScope = ProviderScope.TRANSIENT
):
    """可注入装饰器"""
    def decorator(cls: Type[T]) -> Type[T]:
        cls._injectable_scope = scope
        cls._injectable_registered = False
        return cls
    return decorator

def inject(interface: Type[T]) -> Callable[[...], T]:
    """注入参数装饰器"""
    def decorator(func: Callable) -> Callable:
        sig = inspect.signature(func)
        params = {}
        
        for param_name, param in sig.parameters.items():
            if param.annotation == interface:
                params[param_name] = param
        
        async def wrapper(*args, **kwargs):
            # 从容器获取依赖
            instance = container.resolve(interface)
            kwargs.update(params)
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator

# 使用示例
@injectable(scope=ProviderScope.SESSION)
class MyService:
    def __init__(
        self,
        event_bus: EventBus,  # 自动注入
        repository: MyRepository  # 自动注入
    ):
        self.event_bus = event_bus
        self.repository = repository
    
    @inject(EventBus)
    async def do_something(self, event_bus: EventBus):
        await event_bus.publish(...)
```

## 六、测试支持

```python
class MockContainer(Container):
    """测试用容器"""
    
    def __init__(self):
        super().__init__()
        self._mocks: Dict[Type, Any] = {}
    
    def mock(self, interface: Type[T], instance: T) -> 'MockContainer':
        """注册模拟对象"""
        self._mocks[interface] = instance
        return self
    
    def resolve(self, interface: Type[T]) -> T:
        """优先返回模拟对象"""
        if interface in self._mocks:
            return self._mocks[interface]
        return super().resolve(interface)
    
    def verify(self, interface: Type) -> MockVerifier:
        """验证调用"""
        return MockVerifier(self._mocks.get(interface))
    
    def reset(self) -> None:
        """重置所有模拟"""
        self._mocks.clear()

# 测试示例
def test_my_service():
    container = MockContainer()
    container.mock(EventBus, MockEventBus())
    container.mock(MyRepository, MockRepository())
    
    service = container.resolve(MyService)
    # ...
```

## 七、作用域管理

```python
class ScopedContainer:
    """作用域容器管理器"""
    
    def __init__(self, root_container: Container):
        self._root = root_container
        self._scopes: Dict[str, Container] = {}
    
    def get_session_scope(self, session_id: str) -> Container:
        """获取会话作用域"""
        if session_id not in self._scopes:
            self._scopes[session_id] = self._root.create_child()
            self._configure_session_scope(self._scopes[session_id], session_id)
        return self._scopes[session_id]
    
    def _configure_session_scope(
        self,
        container: Container,
        session_id: str
    ) -> None:
        """配置会话作用域"""
        container.register_instance(SessionContext, SessionContext(session_id))
    
    def close_session_scope(self, session_id: str) -> None:
        """关闭会话作用域"""
        if session_id in self._scopes:
            self._scopes[session_id].clear()
            del self._scopes[session_id]
    
    def close_all(self) -> None:
        """关闭所有作用域"""
        for scope in self._scopes.values():
            scope.clear()
        self._scopes.clear()
```

## 八、配置示例

```python
# config.yaml
di:
  default_scope: "transient"
  
  services:
    EventBus:
      implementation: "LocalEventBus"
      scope: "singleton"
    
    RoleRepository:
      implementation: "RoleRepositoryImpl"
      scope: "singleton"
    
    RuleEngine:
      implementation: "RuleEngineImpl"
      scope: "session"
    
    AIEngine:
      implementation: "AIEngineImpl"
      scope: "session"

# 加载配置
def load_container_config(config: Config) -> Container:
    container = Container()
    
    for name, service_config in config.di.services.items():
        interface = resolve_type(name)
        implementation = resolve_type(service_config.implementation)
        scope = ProviderScope(service_config.scope)
        
        container.register(interface, implementation, scope)
    
    return container
```
