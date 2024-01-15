#![no_std]

multiversx_sc::imports!();
multiversx_sc::derive_imports!();

#[multiversx_sc::contract]
pub trait WalletContract {
    #[init]
    fn init(&self) {}

    #[endpoint]
    fn upgrade(&self) {}

    #[endpoint]
    fn add_account(&self, account: ManagedBuffer) {
        let mut account_balance = self.account_balance();
        let mut account_history = self.account_history();
        require!(
            account_balance.get(&account).is_none(),
            "Account already exists"
        );
        account_balance.insert(account.clone(), BigUint::from(0u32));
        account_history.insert(account.clone(), Vec::new());
    }

    #[endpoint]
    #[only_owner]
    fn mint(&self, account: ManagedBuffer, amount: BigUint) {
        let mut account_balance = self.account_balance();
        let mut account_history = self.account_history();
        let mut balance = account_balance.get(&account).unwrap_or(BigUint::from(0u32));
        balance += amount.clone();
        account_balance.insert(account.clone(), balance);
        let mut history = account_history.get(&account).unwrap_or(Vec::new());
        history.push((
            amount.clone(),
            ManagedBuffer::new_from_bytes("Mint".as_bytes()),
        ));
        account_history.insert(account.clone(), history);
    }

    #[endpoint]
    fn transfer(&self, from: ManagedBuffer, to: ManagedBuffer, amount: BigUint) {
        let mut account_balance = self.account_balance();
        let mut account_history = self.account_history();
        let mut from_balance = account_balance
            .get(&from)
            .expect("From address doesn't exist");
        let mut to_balance = account_balance
            .get(&to)
            .expect("To address doesn't exist");
        require!(
            from_balance >= amount.clone(),
            "Insufficient balance for transfer"
        );
        from_balance -= amount.clone();
        to_balance += amount.clone();
        account_balance.insert(from.clone(), from_balance);
        account_balance.insert(to.clone(), to_balance);
        let mut from_history = account_history.get(&from).unwrap_or(Vec::new());
        let mut to_history = account_history.get(&to).unwrap_or(Vec::new());
        let mut transfer_name = ManagedBuffer::new_from_bytes("Transfer to ".as_bytes());
        transfer_name.append(&to);
        from_history.push((
            amount.clone(),
            transfer_name,
        ));
        let mut receive_name = ManagedBuffer::new_from_bytes("Receive from ".as_bytes());
        receive_name.append(&from);
        to_history.push((
            amount.clone(),
            receive_name,
        ));
        account_history.insert(from.clone(), from_history);
        account_history.insert(to.clone(), to_history);
    }

    #[endpoint]
    fn get_account_balance(&self, account: ManagedBuffer) -> BigUint {
        let account_balance = self.account_balance();
        let balance = account_balance.get(&account).unwrap_or(BigUint::from(0u32));
        balance
    }

    #[endpoint]
    fn get_account_history(&self, account: ManagedBuffer) -> Vec<(BigUint, ManagedBuffer)> {
        let account_history = self.account_history();
        let history = account_history.get(&account).unwrap_or(Vec::new());
        history
    }

    #[view(getAccountBalance)]
    #[storage_mapper("account_balance")]
    fn account_balance(&self) -> MapMapper<ManagedBuffer, BigUint>;

    #[view(getAccountHistory)]
    #[storage_mapper("account_history")]
    fn account_history(&self) -> MapMapper<ManagedBuffer, Vec<(BigUint, ManagedBuffer)>>;
}

