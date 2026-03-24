"""Dependency Injection Container."""
from __future__ import annotations

import inspect
from abc import ABC, abstractmethod
from enum import Enum
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Optional,
    Type,
    TypeVar,
)

T = TypeVar("T")


class ProviderScope(Enum):
    """Provider scope enumeration."""
    
    SINGLETON = "singleton"
    SESSION = "session"
    TRANSIENT = "transient"


class Provider(ABC, Generic[T]):
    """Abstract base class for providers."""
    
    @abstractmethod
    def get(self) -> T:
        """Get an instance."""
        pass
    
    @abstractmethod
    def dispose(self, instance: T) -> None:
        """Dispose an instance."""
        pass


class SingletonProvider(Provider[T]):
    """Singleton provider - returns the same instance."""
    
    def __init__(self, factory: Callable[[], T]):
        self._factory = factory
        self._instance: Optional[T] = None
    
    def get(self) -> T:
        if self._instance is None:
            self._instance = self._factory()
        return self._instance
    
    def dispose(self, instance: T) -> None:
        if hasattr(instance, "dispose"):
            instance.dispose()
        self._instance = None


class TransientProvider(Provider[T]):
    """Transient provider - creates new instance each time."""
    
    def __init__(self, factory: Callable[[], T]):
        self._factory = factory
    
    def get(self) -> T:
        return self._factory()
    
    def dispose(self, instance: T) -> None:
        if hasattr(instance, "dispose"):
            instance.dispose()


class SessionProvider(Provider[T]):
    """Session-scoped provider."""
    
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
        if hasattr(instance, "dispose"):
            instance.dispose()


class Container:
    """Dependency Injection Container."""
    
    def __init__(self) -> None:
        self._providers: Dict[Type, Provider] = {}
        self._factories: Dict[Type, Callable] = {}
        self._scopes: Dict[Type, ProviderScope] = {}
        self._parent: Optional[Container] = None
    
    def register(
        self,
        interface: Type[T],
        implementation: Type[T],
        scope: ProviderScope = ProviderScope.TRANSIENT,
        **kwargs: Any,
    ) -> Container:
        """Register type mapping."""
        def factory() -> T:
            return self._create_instance(implementation, **kwargs)
        
        self._providers[interface] = self._create_provider(factory, scope)
        self._factories[interface] = factory
        self._scopes[interface] = scope
        return self
    
    def register_instance(self, interface: Type[T], instance: T) -> Container:
        """Register an instance (singleton)."""
        self._providers[interface] = SingletonProvider(lambda: instance)
        return self
    
    def register_factory(
        self,
        interface: Type[T],
        factory: Callable[[], T],
        scope: ProviderScope = ProviderScope.TRANSIENT,
    ) -> Container:
        """Register a factory function."""
        self._providers[interface] = self._create_provider(factory, scope)
        self._factories[interface] = factory
        self._scopes[interface] = scope
        return self
    
    def resolve(self, interface: Type[T]) -> T:
        """Resolve a dependency."""
        if interface in self._providers:
            return self._providers[interface].get()
        
        if self._parent:
            return self._parent.resolve(interface)
        
        self._providers[interface] = self._create_provider_from_type(interface)
        return self._providers[interface].get()
    
    def resolve_with_session(self, interface: Type[T], session_id: str) -> T:
        """Resolve session-scoped dependency."""
        if interface not in self._providers:
            raise KeyError(f"Unregistered dependency: {interface}")
        
        provider = self._providers[interface]
        if isinstance(provider, SessionProvider):
            return provider.get(session_id)
        return provider.get()
    
    def create_child(self) -> Container:
        """Create a child container."""
        child = Container()
        child._parent = self
        return child
    
    def clear_session(self, session_id: str) -> None:
        """Clear session-scoped dependencies."""
        for provider in self._providers.values():
            if isinstance(provider, SessionProvider):
                provider.dispose_session(session_id)
    
    def clear(self) -> None:
        """Clear all dependencies."""
        for provider in self._providers.values():
            if isinstance(provider, SingletonProvider):
                provider.dispose(None)
        self._providers.clear()
        self._factories.clear()
        self._scopes.clear()
    
    def _create_provider(
        self,
        factory: Callable[[], T],
        scope: ProviderScope,
    ) -> Provider[T]:
        """Create a provider based on scope."""
        if scope == ProviderScope.SINGLETON:
            return SingletonProvider(factory)
        elif scope == ProviderScope.SESSION:
            return SessionProvider(factory)
        else:
            return TransientProvider(factory)
    
    def _create_provider_from_type(self, cls: Type[T]) -> Provider[T]:
        """Create provider from type."""
        def factory() -> T:
            return self._create_instance(cls)
        return TransientProvider(factory)
    
    def _create_instance(self, cls: Type, **kwargs: Any) -> Any:
        """Create an instance with auto-injection."""
        sig = inspect.signature(cls.__init__)
        params: Dict[str, Any] = {}
        
        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue
            if param_name in kwargs:
                params[param_name] = kwargs[param_name]
            elif param.annotation in self._providers:
                params[param_name] = self.resolve(param.annotation)
        
        return cls(**params)


_container: Optional[Container] = None


def get_container() -> Container:
    """Get the global container instance."""
    global _container
    if _container is None:
        _container = Container()
    return _container


def set_container(container: Container) -> None:
    """Set the global container instance."""
    global _container
    _container = container


def injectable(
    scope: ProviderScope = ProviderScope.TRANSIENT,
) -> Callable[[Type[T]], Type[T]]:
    """Decorator to mark a class as injectable."""
    def decorator(cls: Type[T]) -> Type[T]:
        cls._injectable_scope = scope
        return cls
    return decorator


def inject(interface: Type[T]) -> Callable[[...], T]:
    """Decorator to inject a dependency."""
    def decorator(func: Callable) -> Callable:
        sig = inspect.signature(func)
        params: Dict[str, Any] = {}
        
        for param_name, param in sig.parameters.items():
            if param.annotation == interface:
                params[param_name] = param
        
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            instance = get_container().resolve(interface)
            kwargs.update(params)
            return func(*args, **kwargs)
        
        return wrapper
    return decorator
